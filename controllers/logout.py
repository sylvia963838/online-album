from extensions import connect_to_database
from config import *
from flask import *
from .main import db

# Reference: http://flask.pocoo.org/docs/0.10/quickstart/#sessions

logout = Blueprint('logout', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@logout.route('/logout', methods = ['GET', 'POST'])
def logout_route():
	return redirect(url_for('main.main_route'))