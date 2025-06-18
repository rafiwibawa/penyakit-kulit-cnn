from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import joblib
import numpy as np
import os
from app import db
from app.models import Image
from app.models import ModelLog

bp_latih = Blueprint('latih', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp_latih.route('/data-latih', methods=['GET', 'POST'])
def upload_latih():
    if request.method == 'POST':
        if 'images' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('images') 
        note = request.form.get('note', 'data_latih')
        patient_id = None
        uploaded_by = None

        if not files or files[0].filename == '':
            flash('No selected files')
            return redirect(request.url)

        saved_count = 0
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                new_image = Image(
                    patient_id=patient_id,
                    uploaded_by=uploaded_by,
                    image_path=file_path,
                    upload_time=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    note=note,
                    tipe_data='data_latih'
                )
                db.session.add(new_image)
                saved_count += 1

        if saved_count > 0:
            db.session.commit()
            flash(f'{saved_count} file(s) successfully uploaded and saved.')
        else:
            flash('No valid files were uploaded.')

        return redirect(url_for('latih.upload_latih'))

    images = Image.query.filter_by(tipe_data='data_latih').order_by(Image.upload_time.desc()).all()
    latest_log = ModelLog.query.order_by(ModelLog.trained_at.desc()).first()
    return render_template('latih.html', images=images, latest_log=latest_log)

@bp_latih.route('/train-model', methods=['POST'])
def train_model():
    from train_model import train_image_model
    train_image_model()
    flash('Pelatihan model selesai.', 'success')
    return redirect(url_for('latih.upload_latih'))

@bp_latih.route('/delete-image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    # Hapus file dari sistem file
    if image.image_path and os.path.exists(image.image_path):
        os.remove(image.image_path)

    db.session.delete(image)
    db.session.commit()
    flash('Gambar berhasil dihapus.', 'success')
    return redirect(url_for('latih.upload_latih'))
