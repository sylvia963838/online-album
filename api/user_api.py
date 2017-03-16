from extensions import connect_to_database
from config import *
from flask import *
import re, hashlib, uuid

user_api = Blueprint('user_api', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@user_api.route('/api/v1/user', methods=['GET', 'POST', 'PUT'])
def user_api_route():
	db = connect_to_database()
	cur = db.cursor()

	# GET Request
	if request.method == 'GET':
		# Error: No session
		if 'username' not in session:
			errorsJSON = {
				"errors": [
					{
						"message": "You do not have the necessary credentials for the resource"
					}
				]
			}
			return jsonify(errorsJSON), 401
		# Valid Session:	
		else:
			username = session['username']
			cur.execute("SELECT * FROM User WHERE username = %s", username)
			results = cur.fetchall()
			firstname = results[0]['firstname']
			lastname = results[0]['lastname']
			email = results[0]['email']
			# returna a JSON object
			JSON_Object = {
				"username": username,
				"firstname": firstname,
				"lastname": lastname,
				"email": email
			}
			return jsonify(JSON_Object)

	# POST Request
	elif request.method == 'POST':
		results = request.get_json()

		errorsJSON = {}

		# is_field_error indicates the field error which should be returned immediately
		is_field_error = False

		# Error: Missing a JSON key from the request (empty strings should not throw this error, API route only)
		if 'username' not in results:
			is_field_error = True

		if 'firstname' not in results:
			is_field_error = True

		if 'lastname' not in results:
			is_field_error = True

		if 'password1' not in results:
			is_field_error = True

		if 'password2' not in results:
			is_field_error = True

		if 'email' not in results:
			is_field_error = True

		# If there is lack of field
		if is_field_error == True:
			errorsJSON = {
				"errors": [
					{
						"message": "You did not provide the necessary fields"
					}
				]
			}
			return jsonify(errorsJSON), 422

		# No lack of field
		username = results['username']
		firstname = results['firstname']
		lastname = results['lastname']
		password1 = results['password1']
		password2 = results['password2']
		email = results['email']

		# bool error
		error = False

		# The following errors array can have multiple entries
		errors = []

		cur.execute("SELECT username FROM User")
		usernames = cur.fetchall()
		for item in usernames:
			if item['username'].lower() == username.lower():
				error = True
				errors.append({"message": "This username is taken"})

		if len(username) < 3:
			error = True
			errors.append({"message": "Usernames must be at least 3 characters long"})

		if not re.match("^[a-zA-Z0-9_]+$", username):
			error = True
			errors.append({"message": "Usernames may only contain letters, digits, and underscores"})

		if len(password1) < 8:
			error = True
			errors.append({"message": "Passwords must be at least 8 characters long"})

		if not re.match("^(?=.*[a-zA-Z])(?=.*[0-9])", password1):
			error = True
			errors.append({"message": "Passwords must contain at least one letter and one number"})

		if not re.match("^[a-zA-Z0-9_]+$", password1):
			error = True
			errors.append({"message": "Passwords may only contain letters, digits, and underscores"})

		if password1 != password2:
			error = True
			errors.append({"message": "Passwords do not match"})

		if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
			error = True
			errors.append({"message": "Email address must be valid"})

		if len(username) > 20:
			error = True
			errors.append({"message": "Username must be no longer than 20 characters"})

		if len(firstname) > 20:
			error = True
			errors.append({"message": "Firstname must be no longer than 20 characters"})

		if len(lastname) > 20:
			error = True
			errors.append({"message": "Lastname must be no longer than 20 characters"})

		if len(email) > 40:
			error = True
			errors.append({"message": "Email must be no longer than 40 characters"})

		# If there is error
		if error:
			errorsJSON = {
				"errors": errors
			}
			return jsonify(errorsJSON), 422

		# If no errors, create a new user
		else:
			algorithm = 'sha512'
			password = password1
			salt = uuid.uuid4().hex
			m = hashlib.new(algorithm)
			m.update(str(salt+password).encode('utf-8'))
			password_hash = m.hexdigest()
			password_save = "$".join([algorithm, salt, password_hash])
			cur.execute("INSERT INTO User(username, firstname, lastname, password, email) VALUES (%s, %s, %s, %s, %s)", (username, firstname, lastname, password_save, email))
			
			# return a JSON Object
			JSON_Object = {
				"username": username,
				'firstname': firstname,
				"lastname": lastname,
				"password1": password1,
				"password2": password2,
				"email": email
			}
			return jsonify(JSON_Object), 201

	# PUT Request
	elif request.method == 'PUT':
		requestFields = request.get_json()
		errorsJSON = {}
		errors = []
		firstname = ''
		lastname = ''
		username_request = ''
		email = ''
		password1 = ''

		# Error: No session
		if 'username' not in session:
			errorsJSON = {
				"errors": [
					{
						"message": "You do not have the necessary credentials for the resource"
					}
				]
			}
			return jsonify(errorsJSON), 401
		else:
			username_session = session['username']

		# is_field_error indicates the field error which should be returned immediately
		is_field_error = False

		# Error: Missing a JSON key from the request (empty strings should not throw this error, API route only)
		if 'username' not in requestFields:
			is_field_error = True

		if 'firstname' not in requestFields:
			is_field_error = True

		if 'lastname' not in requestFields:
			is_field_error = True

		if 'password1' not in requestFields:
			is_field_error = True

		if 'password2' not in requestFields:
			is_field_error = True

		if 'email' not in requestFields:
			is_field_error = True

		# If there is lack of field
		if is_field_error == True:
			errorsJSON = {
				"errors": [
					{
						"message": "You did not provide the necessary fields"
					}
				]
			}
			return jsonify(errorsJSON), 422

		# Username sent in request is different from the one in the session
		username_request = requestFields['username']
		if username_request != username_session:
			errorsJSON = {
				"errors": [
					{
						"message": "You do not have the necessary permissions for the resource"
					}
				]
			}
			return jsonify(errorsJSON), 403

		# error (multiple entries)
		error = False
		if requestFields['firstname']:
			firstname = requestFields['firstname']
			if len(firstname) > 20:
				error = True
				errors.append({"message": "Firstname must be no longer than 20 characters"})

		if requestFields['lastname']:
			lastname = requestFields['lastname']
			if len(lastname) > 20:
				error = True
				errors.append({"message": "Lastname must be no longer than 20 characters"})

		if requestFields['password1']:
			password1 = requestFields['password1']
			password2 = requestFields['password2']

			if len(password1) < 8:
				error = True
				errors.append({"message": "Passwords must be at least 8 characters long"})

			if not re.match("^(?=.*[a-zA-Z])(?=.*[0-9])", password1):
				error = True
				errors.append({"message": "Passwords must contain at least one letter and one number"})

			if not re.match("^[a-zA-Z0-9_]+$", password1):
				error = True
				errors.append({"message": "Passwords may only contain letters, digits, and underscores"})

			if password1 != password2:
				error = True
				errors.append({"message": "Passwrods do not match"})

		if requestFields['email']:
			email = requestFields['email']
			if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
				error = True
				errors.append({"message": "Email address must be valid"})

			if len(email) > 40:
				error = True
				errors.append({"message": "Email must be no longer than 40 characters"})

		# If there is error
		if error:
			errorsJSON = {
				"errors": errors
			}
			return jsonify(errorsJSON), 422
		
		# If there is no error, update the database
		else:
			if requestFields['firstname']:
				cur.execute("UPDATE User SET firstname = %s WHERE username = %s", (firstname, username_request))

			if requestFields['lastname']:
				cur.execute("UPDATE User SET lastname = %s WHERE username = %s", (lastname, username_request))

			if requestFields['password1']:
				algorithm = 'sha512'
				password = password1
				salt = uuid.uuid4().hex
				m = hashlib.new(algorithm)
				m.update(str(salt + password).encode('utf-8'))
				password_hash = m.hexdigest()
				password_save = "$".join([algorithm, salt, password_hash])
				cur.execute("UPDATE User SET password = %s WHERE username = %s", (password_save, username_request))

			if requestFields['email']:
				cur.execute("UPDATE User SET email = %s WHERE username = %s", (email, username_request))

			JSON_Object = {
				"username": username_request,
				"firstname": firstname,
				"lastname": lastname,
				"password1": password1,
				"email": email
			}
			return jsonify(JSON_Object)















		