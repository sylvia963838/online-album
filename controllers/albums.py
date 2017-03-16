from flask import *

#import the database initialized in main.py
from .main import db

import os

albums = Blueprint('albums', __name__, template_folder='templates', url_prefix = '/vhwzma2k/p3')

@albums.route('/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():
	cur = db.cursor()
	# GET Method
	if request.method == 'GET':
		is_logged_in = False
		#Check if it is a valid user
		if 'username' in session:
			is_logged_in = True
			username_request = session['username']
		else:
			return redirect(url_for('login.login_route'))

		if username_request == None:
			abort(404)
		if len(username_request) == 0:
			abort(404)
		cur.execute("SELECT username FROM User WHERE username = %s", username_request)
		flag = bool(cur.fetchall())
		if flag == False:
			abort(404)

		cur.execute("SELECT * FROM Album WHERE username = %s", username_request)
		user_albums_own = cur.fetchall()

		cur.execute("SELECT firstname, lastname FROM User WHERE username = %s", username_request)
		results = cur.fetchall()
		firstname = results[0]['firstname']
		lastname = results[0]['lastname']

		options = {
			"edit": True,
			"user_albums_own": user_albums_own,
			"username_request": username_request,
			"is_logged_in": is_logged_in,
			"firstname": firstname,
			"lastname": lastname
		}

	# POST Method
	elif request.method == 'POST':
		is_logged_in = False
		if 'username' in session:
			is_logged_in = True
			username_request = session['username']
		else:
			return redirect(url_for('login.login_route'))
		if username_request == None:
			abort(404)
		if len(username_request) == 0:
			abort(404)
		#add operation
		if request.form['op'] == "add":
			title_request = request.form['title']
			cur = db.cursor()
			cur.execute("INSERT INTO Album VALUES (NULL, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, 'private')", (title_request, username_request))
			db.commit()
			return redirect(url_for('albums.albums_edit_route',username=session['username']))

		#delete operation
		#Note: since we have foreign keys in several tables, when we delete sth. in the parent table, we must first delete in the child table
		elif request.form['op'] == "delete":
			albumid_request = request.form['albumid']
			cur =  db.cursor()
			cur.execute("SELECT picid FROM Contain WHERE albumid = %s", albumid_request)
			photos = cur.fetchall()

			# delete permissions
			cur.execute("DELETE FROM AlbumAccess WHERE albumid = %s", albumid_request)

			# delete the album in Contain
			cur.execute("DELETE FROM Contain WHERE albumid = %s", albumid_request)

			# delete all the photos in the album
			for photo in photos:
				picid = photo['picid']
				cur.execute("SELECT format FROM Photo WHERE picid = %s", picid)
				results = cur.fetchall()
				format = results[0]['format']
				cur.execute("DELETE FROM Photo WHERE picid = %s", picid)
				os.remove('static/images/'+picid+'.'+format)

			# delete the album in Album
			cur.execute("DELETE FROM Album WHERE albumid = %s", albumid_request)

			db.commit()

			return redirect(url_for('albums.albums_edit_route',username=session['username']))
		else:
			abort(404)

		cur.execute("SELECT albumid, title, created, lastupdated, username FROM Album WHERE username = %s" , username_request)
		albums = cur.fetchall()
		if len(albums) == 0:
			abort(404)

		cur.execute("SELECT firstname, lastname FROM User WHERE username = %s", username_request)
		results = cur.fetchall()
		firstname = results[0]['firstname']
		lastname = results[0]['lastname']

		options = {
			"is_logged_in": is_logged_in,
			"edit": True,
			"albums": albums,
			"username_request": username_request,
			"firstname": firstname,
			"lastname": lastname
		}

	return render_template("albums.html", **options)



@albums.route('/albums', methods=['GET'])
def albums_route():
	if request.method == 'GET':
		is_logged_in = False
		is_username_parameter = False
		if 'username' in session:
			is_logged_in = True
			username_request = session['username']
			if 'username' in request.args:
				is_username_parameter = True
		else:
			if 'username' in request.args:
				is_username_parameter = True
				username_request = request.args['username']
			else:
				abort(404)
		if username_request == None:
			abort(404)
		if len(username_request) == 0:
			abort(404)
		cur = db.cursor()
		cur.execute("SELECT username FROM User WHERE username = %s", username_request)
		flag = bool(cur.fetchall())
		if flag == False:
			abort(404)

		cur.execute("SELECT * FROM Album WHERE username = %s AND access = 'public' " , username_request)
		user_public_albums = cur.fetchall()

		cur.execute("SELECT * FROM Album WHERE username = %s", username_request)
		user_albums_own = cur.fetchall()

		cur.execute("SELECT firstname, lastname FROM User WHERE username = %s", username_request)
		results = cur.fetchall()
		firstname = results[0]['firstname']
		lastname = results[0]['lastname']

		'''
		if len(albums) == 0:
			abort(404)
		'''
		options = {
			"edit": False,
			"user_public_albums": user_public_albums,
			"username_request":username_request,
			"user_albums_own": user_albums_own,
			"is_logged_in": is_logged_in,
			"is_username_parameter": is_username_parameter,
			"firstname": firstname,
			"lastname": lastname
		}
	return render_template("albums.html", **options)
	
