from flask import Flask, render_template
import extensions
import controllers
import api
import config

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

# Register the controllers
app.register_blueprint(controllers.album)
app.register_blueprint(controllers.albums)
app.register_blueprint(controllers.pic)
app.register_blueprint(controllers.main)
app.register_blueprint(controllers.user)
app.register_blueprint(controllers.login)
app.register_blueprint(controllers.logout)

app.register_blueprint(api.user_api)
app.register_blueprint(api.login_api)
app.register_blueprint(api.logout_api)
app.register_blueprint(api.album_api)
app.register_blueprint(api.pic_api)

# Set the secret key
app.secret_key = 'A0Zr98j/3yX~/KR~XHH!jmN]LWX/,?RT'

# Listen on external IPs
# For us, listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == '__main__':
    # listen on external IPs
    app.run(host=config.env['host'], port=config.env['port'], debug=True)
