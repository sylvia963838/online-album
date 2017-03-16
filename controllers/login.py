from extensions import connect_to_database
from config import *
from flask import *
from .main import db
import re, hashlib, uuid

login = Blueprint('login', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@login.route('/login', methods = ['GET', 'POST'])
def login_route():
	if 'username' in session:
		return redirect("/vhwzma2k/p3/user/edit")
	return render_template("login.html")


