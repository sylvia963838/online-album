from extensions import connect_to_database
from config import *
from flask import *
import re, hashlib, uuid

login_api = Blueprint('login_api', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@login_api.route('/api/v1/login', methods = ['GET', 'POST'])
def login_api_route():
	db = connect_to_database()
	cur = db.cursor()

	requestFields = request.get_json()

	# Error: Missing Fields
	if 'username' not in requestFields or 'password' not in requestFields:
		errorsJSON = {
			"errors": [
				{
					"message": "You did not provide the necessary fields"
				}
			]
		}
		return jsonify(errorsJSON), 422

	username = requestFields['username']
	password = requestFields['password']

	# Error: Username does not exist
	cur.execute("SELECT username FROM User WHERE username = %s", username)
	results = cur.fetchall()
	if bool(results) == False:
		errorsJSON = {
			"errors": [
				{
					"message": "Username does not exist"
				}
			]
		}
		return jsonify(errorsJSON), 404

	# Error: Password incorrect
	cur.execute("SELECT password FROM User WHERE username = %s", username)
	results = cur.fetchall()
	if bool(results) == True:
		correct_password = results[0]['password']
		salt = results[0]['password'].rsplit('$', 2)[1]
		algorithm = 'sha512'
		m = hashlib.new(algorithm)
		m.update(str(salt+password).encode('utf-8'))
		password_hash = m.hexdigest()
		password_input = "$".join([algorithm,salt,password_hash])

		if password_input != correct_password:
			errorsJSON = {
				"errors": [
					{
						"message": "Password is incorrect for the specified username"
					}
				]
			}
			return jsonify(errorsJSON), 422

		else:
			session['username'] = username
			JSON_Object = {
				"username": username
			}
			return jsonify(JSON_Object)
		





