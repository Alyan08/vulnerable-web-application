import os
import re
import subprocess
from os import name as os_name
from flask import Blueprint, request, render_template


command_injection_bp = Blueprint('command_injections', __name__)


@command_injection_bp.route('/command', methods=['GET', 'POST'])
def create_directory():
    if request.method == 'GET':
        return render_template('command_injection.html')

    msg = None

    try:
        cloud_login = request.form.get('cloud_login')
        command_method = request.form.get('command_method')
    except Exception as e:
        return render_template('command_injection.html', msg=f"Error: {e}")

    try:
        if os.path.exists(f"cloud\\{cloud_login}"):
            raise ValueError("cloud already exists")

        # In the strings bellow you can see the most unsecure operations with os command implementation
        # 1) command = f"mkdir cloud\\{cloud_login}" without any sanitizing of input parameter
        # 2) using shell=True executes the command through a shell, this the main risk of command injection
        if command_method == 'unsecure':
            if os_name == 'nt':
                command = f"mkdir cloud\\{cloud_login}"
            elif os_name == 'posix':
                command = f"mkdir cloud/{cloud_login}"
            else:
                raise ValueError("unknown server OS")

            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            if result.returncode == 0:
                msg = f"cloud folder created | {result.stdout}"
            else:
                msg = result.stdout

        if command_method == 'secure':
            # Bellow is secure code
            # 1) check cloud_login for patterns.
            # This is a very effective method of checking input data against expected patterns
            '''
            if not re.match(r'^[a-zA-Z0-9_]+$', cloud_login):
                raise ValueError("invalid login format")
            '''
            if os_name == 'nt':
                cloud_path = f"cloud\\{cloud_login}"
                # shell=False. The command is executed without using the command line shell in the operating system
                # ['cmd', '/c', 'mkdir', cloud_path] - example of parametrization:
                # when the payload is passed as a parameter, not as part of the request
                result = subprocess.run(['cmd', '/c', 'mkdir', cloud_path], shell=False)
            elif os_name == 'posix':
                cloud_path = f"cloud/{cloud_login}"
                result = subprocess.run(['mkdir', cloud_path], shell=False)
            else:
                raise ValueError("unknown server OS")

            # send only intended messages to the user
            if result.returncode == 0:
                msg = "cloud folder created"
            else:
                msg = "<img src='/static/you_shall_not_pass.jpg'>"

    except Exception as e:
        msg = f"Error: {str(e)}"

    return render_template('command_injection.html', msg=msg)

