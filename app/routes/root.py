from flask import Blueprint, render_template, send_from_directory

from sqlalchemy import func
from app.models import Image 
from app import db

bp_root = Blueprint('root', __name__, url_prefix='/')

@bp_root.route('/')
def index_db(): 
    return render_template( 'login.html' )

@bp_root.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('../uploads', filename)
