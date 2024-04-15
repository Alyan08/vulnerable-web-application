from flask import Flask, render_template
import setup
from vulns import sqli
from vulns import commandi

app = Flask(__name__)
app.debug = False
app.propagate_exceptions = False

setup.create_table()
setup.create_user("admin", "Admin8888", "admin", "Elista", "1111-1111-1111-1111")
setup.create_base_users()
setup.create_cloud_folder()

app.register_blueprint(sqli.sqli_bp, url_prefix='/sqli')
app.register_blueprint(commandi.command_injection_bp)


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, port=5000)


