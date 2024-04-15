from flask import request, Blueprint, render_template
from sqlite3 import connect
from hashlib import md5
from setup import user_exists


sqli_bp = Blueprint('sqli_bp', __name__)


@sqli_bp.route('/login', methods=['GET', 'POST'])
def unsecure_login():
    if request.method == 'GET':
        return render_template('login.html')

    try:
        login = request.form.get('login')
        password = request.form.get('password')
        hashed_password = md5(password.encode()).hexdigest()
        sql_method = request.form.get('sql_method').lower()
        if sql_method not in ["unsecure", "secure"]:
            raise ValueError("Invalid SQL method")
    except Exception as e:
        return render_template('login.html', msg=e)

    conn = None
    try:
        conn = connect('database.db')
        cursor = conn.cursor()
        if sql_method == "unsecure":
            # in the string below we check received login and password using unsecure method
            # because we inject user input directly
            # allowing an attacker to affect our application logic, breaking the SQL query
            sql = f"SELECT login, role  FROM users WHERE login = '{login}' AND password = '{hashed_password}'"
            cursor.execute(sql)
            user_data = cursor.fetchone()

        else:
            # in the string below you see parametrized query
            # it helps to prevent SQL injection by separating the SQL code from the data being used in the query
            # placeholders "?" are used in the SQL string to indicate where the parameters should be inserted
            sql = "SELECT login, role FROM users WHERE login = ? AND password = ?"
            data = (login, hashed_password)
            cursor.execute(sql, data)
            user_data = cursor.fetchone()

        if user_data:
            return render_template('login.html', msg=f"Success login for {user_data[0]} ... resulted SQL Query: {sql}")
        else:
            return render_template('login.html', msg="Wrong credentials")

    except Exception as e:
        return render_template('login.html', msg=f"Error in login request: {e}")
    finally:
        if conn:
            conn.close()


@sqli_bp.route('/search', methods=['GET', 'POST'])
def unsecure_search():
    if request.method == 'GET':
        return render_template('search.html')
    try:
        search_text = request.form.get('search_text')
        sql_method = request.form.get('sql_method').lower()
        if sql_method not in ["unsecure", "secure"]:
            raise ValueError("Invalid SQL method")

    except Exception as e:
        return render_template('search.html', result=f"Error: {e}")

    conn = None
    search_result = ""
    try:
        conn = connect('database.db')
        cursor = conn.cursor()

        if sql_method == "unsecure":
            # in the string below we check received login and password using unsecure method
            # because we inject user input directly
            # allowing an attacker to affect our application logic, breaking the SQL query
            sql = f"SELECT login FROM users WHERE login LIKE '%{search_text}%'"
            cursor.execute(sql)
            data = cursor.fetchall()
            resulting_query = sql

        else:
            # in the string below you see parametrized query
            # it helps to prevent SQL injection by separating the SQL code from the data being used in the query
            # placeholders "?" are used in the SQL string to indicate where the parameters should be inserted
            sql = "SELECT login FROM users WHERE login LIKE ?"
            cursor.execute(sql, ('%' + search_text + '%',))
            data = cursor.fetchall()
            resulting_query = None

        if data:
            search_result = ', '.join(item[0] for item in data)
            return render_template('search.html', result=f"{search_result}", resulting_query=resulting_query)
        else:
            return render_template('search.html', result="users not found")

    except Exception as e:
        print(e)
        return render_template('search.html', result=f"Error in search request: {e}")
    finally:
        if conn:
            conn.close()


@sqli_bp.route('registration', methods=['GET', 'POST'])
def second_order_reg():
    if request.method == 'GET':
        return render_template('registration.html')

    login = request.form.get('login')
    password = request.form.get('password')
    hashed_password = md5(password.encode()).hexdigest()
    city = request.form.get('city')
    credit_card = request.form.get('credit_card')

    conn = None
    try:
        conn = connect('database.db')
        cursor = conn.cursor()

        if user_exists(login):
            raise ValueError("user already exists")
        # in the string below you see parametrized query
        # it helps to prevent SQL injection by separating the SQL code from the data being used in the query
        # placeholders "?" are used in the SQL string to indicate where the parameters should be inserted
        cursor.execute('''INSERT INTO users (login, password, role, city, credit_card)
                          VALUES (?, ?, ?, ?, ?)''', (login, hashed_password, "user", city, credit_card))
        conn.commit()
        return render_template('registration.html', result="success registration!")

        # check:

    except Exception as e:
        print(e)
        return render_template('registration.html', result=f"Error in registration request: {e}")
    finally:
        if conn:
            conn.close()


@sqli_bp.route('/user/city', methods=['GET', 'POST'])
def check_user_city():
    if request.method == 'GET':
        return render_template('users_from_city.html')

    try:
        login = request.form.get('login')
        if not login:
            raise ValueError("Invalid login in search area")

    except Exception as e:
        return render_template('search.html', result=f"Error: {e}")
    conn = None
    try:
        conn = connect('database.db')
        cursor = conn.cursor()

        # in the string below you see parametrized query in first SQL query for receiving user's cite from DB
        # it helps to prevent SQL injection by separating the SQL code from the data being used in the query
        # placeholders "?" are used in the SQL string to indicate where the parameters should be inserted
        # you can not implement SQLi with login parameter, but there is a surprise bellow
        sql = "SELECT city FROM users WHERE login = ?"
        cursor.execute(sql, (login,))
        login_city = cursor.fetchone()

        # in the strings bellow we can see unsecure injecting login_city[0] value into sql query
        # this is the simple example of second-order SQL-injection with stored SQL-injection
        sql = f"SELECT login FROM users WHERE city = '{login_city[0]}'"
        cursor.execute(sql)
        logins = cursor.fetchall()
        search_result = ', '.join(item[0] for item in logins)
        if not search_result:
            result = "users not found"
        else:
            result = search_result

        return render_template('users_from_city.html',
                               result=f"users in the same city as {login}: {result} ... resulted SQL Query: {sql}")

    except Exception as e:
        print(e)
        return render_template('users_from_city.html', result=f"Error in search request: {e}")
    finally:
        if conn:
            conn.close()

