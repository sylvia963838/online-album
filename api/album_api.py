from extensions import connect_to_database
from config import *
from flask import *
import re, hashlib, uuid

album_api = Blueprint('album_api', __name__, template_folder='templates', url_prefix = '/vhwzma2k/p3')

@album_api.route('/api/v1/album/<albumid>', methods=['GET'])
def album_api_route(albumid):
	db = connect_to_database()
	cur = db.cursor()
	albumid = int(albumid)
	# Error: The album must exist
	cur.execute("SELECT * FROM Album WHERE albumid = %s", albumid)
	results = cur.fetchall()
	if bool(results) == False:
		errorsJSON = {
			"errors": [
				{
					"message": "The requested resource could not be found"
				}
			]
		}
		return jsonify(errorsJSON), 404

	cur.execute("SELECT username, access FROM Album WHERE albumid = %s", albumid)
	results = cur.fetchall()
	album_owner = results[0]['username']
	album_access = results[0]['access']

	is_logged_in = False
	username_session = ''
	
	if 'username' in session:
		is_logged_in = True
		username_session = session['username']

	# If album is public, everyone can view the album
	# If album is private, only album owner and people who are given access can view the album
	# Thus, there are two following errors:
	# 1. If not logged in and the album is private, Error "No session"
	# 2. If logged in but no permission (not album_owner and not given access), Error "Logged in but no permissions"

	# Condition 1: If not logged in and the album is private, Error "No session"
	if is_logged_in == False and album_access == 'private':
		errorsJSON = {
			"errors": [
				{
					"message": "You do not have the necessary credentials for the resource"
				}
			]
		}
		return jsonify(errorsJSON), 401

	# Condition 2: If logged in but no permission (not album_owner and not given access), Error "Logged in but no permissions"
	if is_logged_in == True:
		print (username_session, album_owner)
		if username_session != album_owner:
			is_given_access = False
			if album_access == 'public':
				is_given_access = True

			cur.execute("SELECT username FROM AlbumAccess WHERE albumid = %s", albumid)
			usernames = cur.fetchall()
			for item in usernames:
				username = item['username']
				if username == username_session:
					is_given_access = True

			if is_given_access == False:
				errorsJSON = {
					"errors": [
						{
							"message": "You do not have the necessary permissions for the resource"
						}
					]
				}
				return jsonify(errorsJSON), 403

	# If no error, get information of the album
	cur.execute("SELECT * FROM Album WHERE albumid = %s", albumid)
	AlbumAll = cur.fetchall()
	created = AlbumAll[0]['created']
	lastupdated = AlbumAll[0]['lastupdated']
	title = AlbumAll[0]['title']

	# Get all pictures of the specified album
	# Store all the structures of pics
	picsArray = []
	cur.execute("SELECT picid FROM Contain WHERE albumid = %s", albumid)
	pics = cur.fetchall()

	for pic in pics:
		cur.execute("SELECT * FROM Contain WHERE picid = %s", pic['picid'])
		allContain = cur.fetchall()
		pic_sequencenum = allContain[0]['sequencenum']
		pic_caption = allContain[0]['caption']

		cur.execute("SELECT * FROM Photo WHERE picid = %s", pic['picid'])
		allPhoto = cur.fetchall()
		pic_format = allPhoto[0]['format']
		pic_date = allPhoto[0]['date']

		# pic struct
		pic_struct = {
			"albumid": albumid,
			"caption": pic_caption,
			"date": pic_date,
			"format": pic_format,
			"picid": pic['picid'],
			"sequencenum": pic_sequencenum
		}

		picsArray.append(pic_struct)

	JSON_Object = {
		"access": album_access,
		"albumid": albumid,
		"created": created,
		"lastupdated": lastupdated,
		"pics": picsArray,
		"title": title,
		"username": album_owner
	}

	return jsonify(JSON_Object)







