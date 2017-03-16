from extensions import connect_to_database
from config import *
from flask import *

# Reference: http://flask.pocoo.org/docs/0.10/quickstart/#sessions

logout_api = Blueprint('logout_api', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@logout_api.route('/api/v1/logout', methods=['GET', 'POST'])
def logout_api_route():
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
		session.pop('username', None)
		return jsonify(), 204