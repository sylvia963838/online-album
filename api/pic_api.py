from extensions import connect_to_database
from config import *
from flask import *
import re, hashlib, uuid

pic_api = Blueprint('pic_api', __name__, template_folder='templates', url_prefix = "/vhwzma2k/p3")

@pic_api.route('/api/v1/pic/<picid>', methods=['GET', 'PUT'])
def pic_api_route(picid):
	db = connect_to_database()
	cur = db.cursor()

	if request.method == 'GET':

		# Error: The picture must exist
		cur.execute("SELECT picid FROM Contain WHERE picid = %s", picid)
		results = cur.fetchall()
		if len(results) == 0:
			errorsJSON = {
				"errors": [
					{
						"message": "The requested resource could not be found"
					}
				]
			}
			return jsonify(errorsJSON), 404

		cur.execute("SELECT albumid FROM Contain WHERE picid = %s", picid)
		results = cur.fetchall()
		albumid = results[0]['albumid']
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

		# If no error, get information of the picture (this pic, next pic, prev pic)
		cur.execute("SELECT format FROM Photo WHERE picid = %s", picid)
		results = cur.fetchall()
		this_pic_format = results[0]['format']

		cur.execute("SELECT caption FROM Contain WHERE picid = %s", picid)
		results = cur.fetchall()
		this_pic_caption = results[0]['caption']

		cur.execute("SELECT sequencenum FROM Contain WHERE picid = %s", picid)
		results = cur.fetchall()
		sequencenum = results[0]['sequencenum']

		cur.execute("SELECT sequencenum FROM Contain WHERE albumid = %s ORDER BY sequencenum DESC", albumid)
		sequencenum_desc = cur.fetchall()
		maxSequencenum = sequencenum_desc[0]['sequencenum']

		cur.execute("SELECT sequencenum FROM Contain WHERE albumid = %s ORDER BY sequencenum", albumid)
		sequencenum_asce = cur.fetchall()
		minSequencenum = sequencenum_asce[0]['sequencenum']

		isValid_next_pic = False
		isValid_prev_pic = False

		for i, seq in enumerate(sequencenum_asce):
			if seq['sequencenum'] == sequencenum:
				seq_index = i

		prev_picid = ''
		next_picid = ''

		if sequencenum != maxSequencenum:
			next_pic_seqnum = sequencenum_asce[seq_index+1]['sequencenum']
			cur.execute("SELECT picid FROM Contain WHERE sequencenum = %s", next_pic_seqnum)
			results = cur.fetchall()
			next_picid = results[0]['picid']

			cur.execute("SELECT format FROM Photo WHERE picid = %s", next_picid)
			results = cur.fetchall()
			next_pic_format = results[0]['format'] 

			isValid_next_pic = True

		if sequencenum != minSequencenum:
			prev_pic_seqnum = sequencenum_asce[seq_index - 1]['sequencenum']
			cur.execute("SELECT picid FROM Contain WHERE sequencenum = %s", prev_pic_seqnum)
			results = cur.fetchall()
			prev_picid = results[0]['picid']

			cur.execute("SELECT format FROM Photo WHERE picid = %s", prev_picid)
			results = cur.fetchall()
			prev_pic_format = results[0]['format']

			isValid_prev_pic = True

		JSON_Object = {
			"albumid": albumid,
			"caption": this_pic_caption,
			"format": this_pic_format,
			"next": next_picid,
			"picid": picid,
			"prev": prev_picid
		}
		return jsonify(JSON_Object), 200

	elif request.method == 'PUT':
		# Not logged in 
		if 'username' not in session:
			errorsJSON = {
				"errors": [
					{
						"message": "You do not have the necessary credentials for the resource"
					}
				]
			}
			return jsonify(errorsJSON), 401

		# Logged in
		else:
			
			requestFields = request.get_json()
			username_session = session['username']
	
			# Error: Missing Fields
			is_field_error = False
			if 'albumid' not in requestFields:
				is_field_error = True

			if 'caption' not in requestFields:
				is_field_error = True

			if 'picid' not in requestFields:
				is_field_error = True

			if is_field_error == True:
				errorsJSON = {
					"errors": [
						{
							"message": "You did not provide the necessary fields"
						}
					]
				}
				return jsonify(errorsJSON), 422

			albumid = requestFields['albumid']


			# Error: The picture must exist
			cur.execute("SELECT * FROM Contain WHERE picid = %s", picid)
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
			
			# Error: Picture is not a member of the album
			cur.execute("SELECT * FROM Contain WHERE albumid = %s and picid = %s", (albumid, picid))
			results = cur.fetchall()
			if bool(results) == False:
				errorsJSON = {
					"errors": [
						{
							"message": "Picture is not part of this album"
						}
					]
				}
				return jsonify(errorsJSON), 422

			# Error: 403 Logged in but no permission
			cur.execute("SELECT * FROM Album WHERE albumid = %s", albumid)
			results = cur.fetchall()
			album_owner = results[0]['username']
			album_access = results[0]['access']
			
			if username_session != album_owner:
				is_given_access = False
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
				


			# No error
			new_caption = requestFields['caption']
			

			cur.execute("UPDATE Contain SET caption = %s WHERE picid = %s", (new_caption, picid))
			cur.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = %s", albumid)

			JSON_Object = {
				"albumid": albumid,
				"caption": new_caption,
				"picid": picid
			}

			return jsonify(JSON_Object), 200






