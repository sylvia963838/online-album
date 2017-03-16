from extensions import connect_to_database
from config import *
from flask import *
from .main import db
import re, hashlib, uuid

user = Blueprint('user', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@user.route('/user', methods = ['GET', 'POST'])
def user_route():
	# If a session already exists, redirect the user to /user/edit
	if "username" in session:
		return redirect ("/vhwzma2k/p3/user/edit")

	return render_template("user.html")

@user.route('/user/edit', methods = ['GET', 'POST'])
def user_edit_route():
	# If a session does not exist, redirect the user to /login
	if 'username' not in session:
		return redirect ("/vhwzma2k/p3/login")

	return render_template("user_edit.html")







