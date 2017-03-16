from extensions import connect_to_database

from config import *

from flask import *

# Initialize db then reuse the database for rest of project
db = connect_to_database()

main = Blueprint('main', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@main.route('/')
def main_route():
	cur = db.cursor()
	is_logged_in = False
	# user not logged in 
	if 'username' not in session:
		cur.execute('SELECT username FROM User')
		username_list = cur.fetchall()
		cur.execute("SELECT * FROM Album WHERE access = 'public'")
		public_album_list = cur.fetchall()
		is_logged_in = False

		options = {
			"users": username_list,
			"public_album_list": public_album_list,
			"is_logged_in": False,
			"is_home_page": True
		}
		return render_template("base.html", **options)

	# user has logged in
	else:
		username = session['username']
		is_logged_in = True
		# firstname and lastname
		cur.execute("SELECT * FROM User WHERE username = %s", username)
		results = cur.fetchall()
		firstname = results[0]['firstname']
		lastname = results[0]['lastname']

		public_albums_exist = False
		user_private_albums_exist = False
		private_albums_with_access_exist = False

		# public albums
		cur.execute("SELECT * FROM Album WHERE access = 'public'")
		public_albums = cur.fetchall()
		if len(public_albums) != 0:
			public_albums_exist = True

		# user's private albums
		cur.execute("SELECT * FROM Album WHERE username = %s and access = 'private' ", username)
		user_private_albums = cur.fetchall()
		if len(user_private_albums) != 0:
			user_private_albums_exist = True

		# private albums with access by the owner
		cur.execute("SELECT albumid FROM AlbumAccess WHERE username = %s", username)
		results = cur.fetchall()
		if len(results) != 0:
			private_albums_with_access_exist = True
		private_albums_with_access = []
		for result in results:
			cur.execute("SELECT * FROM Album WHERE albumid = %s", result['albumid'])
			album = cur.fetchall()
			private_albums_with_access.append(album[0])

		if is_logged_in:
			session['firstname'] = firstname
			session['lastname'] =  lastname

		options = {
			"is_logged_in": True,
			"username": username,
			"firstname": firstname,
			"lastname": lastname,
			"public_albums": public_albums,
			"user_private_albums": user_private_albums,
			"private_albums_with_access": private_albums_with_access,
			"public_albums_exist": public_albums_exist,
			"user_private_albums_exist": user_private_albums_exist,
			"private_albums_with_access_exist": private_albums_with_access_exist,
			"is_home_page": True
		}
		return render_template("base.html", **options)

