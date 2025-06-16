from flask import Blueprint, render_template
from sqlalchemy import func
from app.models import Image 
from app import db

bp_dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp_dashboard.route('/index')
def index():
    # Ambil jumlah per label untuk data_latih
    data_latih = (
        db.session.query(Image.note, func.count(Image.id))
        .filter(Image.tipe_data == 'data_latih', Image.note != None)
        .group_by(Image.note)
        .all()
    )

    # Ambil jumlah per label untuk data_uji
    data_uji = (
        db.session.query(Image.note, func.count(Image.id))
        .filter(Image.tipe_data == 'data_uji', Image.note != None)
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