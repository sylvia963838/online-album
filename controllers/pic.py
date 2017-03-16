from flask import *
from .main import db

pic = Blueprint('pic', __name__, template_folder='templates', url_prefix='/vhwzma2k/p3')

@pic.route('/pic', methods = ['GET', 'POST'])
def pic_route():
	return render_template("album_new.html")