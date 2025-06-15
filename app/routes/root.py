from flask import Blueprint, render_template, send_from_directory

from sqlalchemy import func
from app.models import Image 
from app import db

bp_root = Blueprint('root', __name__, url_prefix='/')

@bp_root.route('/')
def index_db():
    # Ambil jumlah per label untuk data_latih
    data_latih = (
        db.session.query(Image.note, func.count(Image.id))
        .filter(Image.tipe_data == 'data_latih')
        .group_by(Image.note)
        .all()
    )

    # Ambil jumlah per label untuk data_uji
    data_uji = (
        db.session.query(Image.note, func.count(Image.id))
        .filter(Image.tipe_data == 'data_uji')
        .group_by(Image.note)
        .all()
    )

    # Ubah hasil query jadi dict
    chart_data_latih = {note: count for note, count in data_latih}
    chart_data_uji = {note: count for note, count in data_uji} 
     
    return render_template(
        'dashboard.html',
        chart_data_latih=chart_data_latih,
        chart_data_uji=chart_data_uji
    )

@bp_root.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('../uploads', filename)
