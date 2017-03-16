from flask import *
from .main import db
import os
import hashlib
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif', 'PNG', 'JPG', 'BMP', 'GIF'])

album = Blueprint('album', __name__, template_folder='templates', url_prefix = '/vhwzma2k/p3')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@album.route('/album/edit', methods = ['GET', 'POST'])
def album_edit_route():
	is_logged_in = False
	if 'username' not in session:
		return redirect(url_for('login.login_route'))
	else:
		is_logged_in = True
		if 'albumid' not in request.args:
			abort(404)
		albumid = request.args['albumid']
		if albumid == None:
			abort(404)
		if len(albumid) == 0:
			abort(404)
	
	albumid = request.args['albumid']
	cur = db.cursor()

	# check if the logged in user is the owner of the current album
	if is_logged_in == True:
		cur.execute("SELECT username FROM Album WHERE albumid = %s", albumid)
		res = cur.fetchall()
		owner = res[0]['username']
		if owner != session['username']:
			abort(403)

	if request.method == 'GET':
		cur.execute("SELECT albumid FROM Album WHERE albumid = %s", albumid)
		flag = bool(cur.fetchall())
		if flag == False:
			abort(404)

		# select picid ordered by sequencenum
		cur.execute("SELECT picid, sequencenum FROM Contain WHERE albumid = %s", albumid)
		pics = cur.fetchall()

		# create an empty list to store the picture name (filename)
		picsname = []
		for pic in pics:
			cur.execute("SELECT picid, format FROM Photo WHERE picid = %s", pic['picid'])
			filename = cur.fetchall()
			picsname.append(filename[0])

		cur.execute("SELECT title, username FROM Album WHERE albumid = %s", albumid)
		results = cur.fetchall()

		albumtitle = results[0]['title']
		#username = results[0]['username']
		username = session['username']

		# Determine whether the album is private or public
		cur.execute("SELECT access FROM Album WHERE albumid = %s", albumid)
		results = cur.fetchall()
		access = results[0]['access']
		is_album_public = False
		is_album_private = False
		if access == 'public':
			is_album_public = True
		else:
			is_album_private = True

		cur.execute("SELECT username FROM AlbumAccess WHERE albumid = %s", albumid)
		users_given_permission = cur.fetchall()

	elif request.method == 'POST':
		# Determine whether the album is private or public
		cur.execute("SELECT access FROM Album WHERE albumid = %s", albumid)
		results = cur.fetchall()
		access = results[0]['access']
		is_album_public = False
		is_album_private = False
		if access == 'public':
			is_album_public = True
		else:
			is_album_private = True

		# select picid ordered by sequencenum
		cur.execute("SELECT picid, sequencenum FROM Contain WHERE albumid = %s", albumid)
		pics = cur.fetchall()

		# create an empty list to store the picture name (filename)
		picsname = []
		for pic in pics:
			cur.execute("SELECT picid, format FROM Photo WHERE picid = %s", pic['picid'])
			filename = cur.fetchall()
			picsname.append(filename[0])

		cur.execute("SELECT title, username FROM Album WHERE albumid = %s", albumid)
		results = cur.fetchall()

		albumtitle = results[0]['title']
		#username = results[0]['username']
		username = session['username']

		cur.execute("SELECT username FROM AlbumAccess WHERE albumid = %s", albumid)
		users_given_permission = cur.fetchall()

		# add pictures to the album
		# follow the tutorial on http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
		# check if the post request has the file part
		if request.form['op'] == 'add':
			if 'file' not in request.files:
				flash('No file part')
				return redirect(url_for('album.album_edit_route', albumid=albumid))
			file = request.files['file']
			# if user does not select file, browser also
			# submit an empty part without file name
			if file.filename == ' ':
				flash('No selected file')
				return redirect(url_for('album.album_edit_route',albumid=albumid))
			if file and allowed_file(file.filename):
				filename_total = secure_filename(file.filename)

				# generate a unique hash for each picture
				# suppose that filename is filename.pic_format
				m = hashlib.md5((str(albumid) + filename_total).encode('utf-8'))
				picid = m.hexdigest()
				filename_split = filename_total.split('.')
				filename = filename_split[0]
				pic_format = filename_split[1]

				# get the current maximum sequencenum
				# get the dict for sequence in descending order
				cur.execute("SELECT sequencenum FROM Contain ORDER BY sequencenum DESC")
				results = cur.fetchall()
				sequencenum = results[0]['sequencenum'] + 1

				# change the database
				# update the lastupdate in Table Album
				cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)

				# add photo to the Contain
				cur.execute("INSERT INTO Photo VALUES(%s, %s, CURRENT_TIMESTAMP)", (picid, pic_format))
				cur.execute("INSERT INTO Contain VALUES(%s, %s, %s, ' ')", (sequencenum, albumid, picid))
				db.commit()

				# save file to os
				filename_save = secure_filename(str(picid) + '.' + pic_format)
				file.save(os.path.join(UPLOAD_FOLDER, filename_save))
			else:
				abort(404)

			return redirect(url_for('album.album_edit_route',albumid=albumid))

		elif request.form['op'] == 'delete':
			picid = request.form['picid']

			# remove file from os
			cur.execute("SELECT format FROM Photo WHERE picid = %s", picid)
			results = cur.fetchall()
			pic_format = results[0]['format']

			# delete from the database
			cur.execute("DELETE FROM Contain WHERE picid = %s", picid)
			cur.execute("DELETE FROM Photo WHERE picid = %s", picid)

			os.remove(UPLOAD_FOLDER + picid + '.' + pic_format)

			# update the lastupdate in Table Album
			cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)

			db.commit()

			return redirect(url_for('album.album_edit_route',albumid=albumid))

		# modify an album's public/private access
		elif request.form['op'] == 'access':
			# if it is a public album originally
			if is_album_public:
				if request.form['access'] == 'private':
					cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)
					cur.execute("UPDATE Album SET access = 'private' WHERE albumid = %s", albumid)
			else:
				if request.form['access'] == 'public':
					cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)
					cur.execute("UPDATE Album SET access = 'public' WHERE albumid = %s", albumid)
					cur.execute("DELETE FROM AlbumAccess WHERE albumid = %s", albumid)

			return redirect(url_for('album.album_edit_route',albumid=albumid))

		# Grant a user permission
		elif request.form['op'] == 'grant':
			if is_album_private:
				username_grant = request.form['username']
				cur.execute("SELECT username FROM User WHERE username = %s", username_grant)
				results = cur.fetchall()
				if bool(results):
					cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)
					cur.execute("INSERT INTO AlbumAccess(albumid, username) VALUES (%s, %s)", (albumid, username_grant))
			return redirect(url_for('album.album_edit_route',albumid=albumid))

		elif request.form['op'] == 'revoke':
			if is_album_private:
				username_revoke = request.form['username']
				cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)
				cur.execute("DELETE FROM AlbumAccess WHERE albumid = %s AND username = %s", (albumid, username_revoke))
			return redirect(url_for('album.album_edit_route',albumid=albumid))

		else:
			abort(404)
	cur.execute("SELECT firstname, lastname FROM User WHERE username = %s", username)
	results = cur.fetchall()
	firstname = results[0]['firstname']
	lastname = results[0]['lastname']

	if is_logged_in:
		session['firstname'] = firstname
		session['lastname'] = lastname

	options = {
		"edit": True,
		"albumtitle": albumtitle,
		"picsname": picsname,
		"albumid": albumid,
		"username": username,
		"is_logged_in": is_logged_in,
		"is_album_public":is_album_public,
		"is_album_private": is_album_private,
		"users_given_permission": users_given_permission,
		"is_home_page": False,
		"firstname": firstname,
		"lastname": lastname
	}




	return render_template("album.html", **options)

@album.route('/album', methods = ['GET'])
def album_route():
	return render_template("album_new.html")
