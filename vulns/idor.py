from flask import Blueprint, request, render_template, session
from sqlite3 import connect

idor_bp = Blueprint('idor_bp', __name__)


@idor_bp.route('/idor', methods=['GET'])
def idor_page():
    if not session.get('login'):
        return render_template('idor.html',
                               msg="You are not authorized. Come back after authentication: ",
                               link=f"http://127.0.0.1:5000/auth",
                               link_name="go to authentication")

    conn = None
    try:
        conn = connect('database.db')
        cursor = conn.cursor()
        sql = "SELECT user_id, role FROM users WHERE login = ?"
        cursor.execute(sql, (session.get('login'),))
        user_data = cursor.fetchone()
        user_id = user_data[0]

        link = f"http://127.0.0.1:5000/idor/{user_id}/credit_card/"

        text = """
            &emsp;IDOR, or Insecure Direct Object References, is a web application vulnerability<br>
            &emsp;where an attacker can directly access objects bypassing access controls,<br>
            &emsp;allowing unauthorized access to resources or functionalities.<br><br>
            &emsp;Example:<br>
            &emsp;1) you are authorized on the website.<br>
            &emsp;2) you can access your credit card data via the link.<br>
            """

        return render_template('idor.html', link=link, link_name="check your credit card", text=text)

    except Exception as e:
        print(e)
        return render_template('idor.html', msg=f"Error: {e}")
    finally:
        if conn:
            conn.close()


@idor_bp.route('/idor/<int:user_id>/credit_card/', methods=['GET'])
def idor_credit_card(user_id):
    if not session.get('login'):
        return render_template('idor.html', msg="You are not authorized")

    conn = None
    try:
        conn = connect('database.db')
        cursor = conn.cursor()
        sql = "SELECT login, credit_card, role FROM users WHERE user_id = ?"
        cursor.execute(sql, (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            msg = f"""&emsp;Your are authorized as {session.get('login')}
                        No card found for user with identifier {user_id}"""
        else:
            msg = f"""
                &emsp;You are authorized as {session.get('login')}<br>
                &emsp;Your credit card info: <br>
                &emsp;Card holder name: {user_data[0]} , card number: {user_data[1]}
                """

        text = """
                   &emsp;If you look at the URL, you can see the identifier.<br>
                   &emsp;The IDOR vulnerability occurs when you can access others' 
                   data through an identifier enumeration method.<br>
                   &emsp;Try to access information about other users' cards.<br><br>
                   &emsp;Cause of the vulnerability:<br>
                   &emsp;Although the application checks the user session, <br>
                   &emsp;there is no access control check for an authorized user <br>
                   &emsp; accessing another user's credit card information with different identifiers.<br>
                   &emsp; Try accessing identifiers within a small range (1111-1119).<br>
                   """

        return render_template('idor.html', msg=msg, text=text)

    except Exception as e:
        print(e)
        return render_template('idor.html', msg=f"Error: {e}")
    finally:
        if conn:
            conn.close()
