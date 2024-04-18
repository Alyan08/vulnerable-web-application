from flask import Flask, render_template, session
from flask_session import Session
import setup
from vulns import (sqli,
                   commandi,
                   ssti,
                   authenticate,
                   idor)
import os

app = Flask(__name__)
app.debug = False
app.propagate_exceptions = False
app.config['SECRET_KEY'] = 'i_am_the_secret_key_value'
os.environ['rsa_key'] = 'i_am_the_secret_rsa_key_value'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

setup.create_table()
setup.create_user("admin", "Admin8888", "admin", "Elista", "1111-1111-1111-1111")
setup.create_base_users()
setup.create_cloud_folder()

app.register_blueprint(sqli.sqli_bp, url_prefix='/sqli')
app.register_blueprint(commandi.command_injection_bp)
app.register_blueprint(ssti.ssti_bp)
app.register_blueprint(authenticate.auth_bp)
app.register_blueprint(idor.idor_bp)


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, port=5000)


