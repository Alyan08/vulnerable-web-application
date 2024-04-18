from flask import Blueprint, request, render_template, session
from sqlite3 import connect
from hashlib import md5


auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        return render_template('authenticate.html')

    try:
        login = request.form.get('login')
        password = request.form.get('password')
        hashed_password = md5(password.encode()).hexdigest()
    except Exception as e:
        return render_template('authenticate.html', msg=f"please enter login and password. error: {e}")

    conn = None
    try:
        conn = connect('database.db')
        cursor = conn.cursor()
        sql = "SELECT login, role FROM users WHERE login = ? AND password = ?"
        data = (login, hashed_password)
        cursor.execute(sql, data)
        user_data = cursor.fetchone()

        if user_data:
            session['login'] = user_data[0]
            session['role'] = user_data[1]
            return render_template('authenticate.html', msg="success")
        else:
            raise ValueError("wrong credentials")

    except Exception as e:
        return render_template('authenticate.html', msg=f"Error in login request: {e}")
    finally:
        if conn:
            conn.close()
