from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime 
import joblib 
import os
import uuid
from app import db 
from app.models import Image
from app.models import Patient, Prediction, Diagnosis
from utils.feature_extractor import extract_features

bp_diagnoses = Blueprint('diagnoses', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp_diagnoses.route('/diagnoses', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # 1. Simpan data pasien
            name = request.form['name']
            gender = request.form['gender']
            birth_date = request.form['birth_date']
            phone = request.form['phone']
            address = request.form['andress']

            # Konversi gender ke enum DB (male/female)
            gender = 'male' if gender.lower() == 'laki-laki' else 'female'

            new_patient = Patient(
                name=name,
                gender=gender,
                birth_date=birth_date,
                phone=phone,
                address=address,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_patient)
            db.session.flush()  # Agar ID bisa langsung dipakai

            patient_id = new_patient.id
            user_id = session.get('user_id')  # pastikan user sudah login

            # 2. Simpan semua gambar
            images = request.files.getlist('images')
            for img_file in images:
                if img_file:
                    filename = secure_filename(img_file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    img_file.save(save_path)

                    new_image = Image(
                        patient_id=patient_id,
                        uploaded_by=user_id,
                        image_path=save_path,
                        upload_time=datetime.utcnow(),
                        tipe_data='data_uji',
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(new_image)
                    db.session.flush()

                    # 3. Ekstrak fitur & prediksi
                    features = extract_features(save_path)
                    if features is not None:
                        model = joblib.load('model/random_forest.pkl')
                        encoder = joblib.load('model/label_encoder.pkl')
                        prediction = model.predict([features])[0]
                        label = encoder.inverse_transform([prediction])[0]
                        confidence = max(model.predict_proba([features])[0])

                        new_pred = Prediction(
                            image_id=new_image.id,
                            model_version="v1",
                            predicted_label=label,
                            confidence=confidence,
                            prediction_time=datetime.utcnow(),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.session.add(new_pred)

            # 4. Simpan diagnosa (berdasarkan gambar terakhir)
            new_diag = Diagnosis(
                patient_id=patient_id,
                user_id=user_id,
                diagnosis=f"Diagnosis otomatis berdasarkan gambar",  # bisa diisi manual jika perlu
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_diag)

            db.session.commit()
            flash("✅ Diagnosis berhasil disimpan.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Terjadi kesalahan: {e}", "danger")

        return redirect(url_for('diagnoses.index'))
    
    patients = Patient.query.all()
    return render_template('diagnoses.html', patients=patients)

@bp_diagnoses.route('/diagnoses/<int:patient_id>')
def detail(patient_id):
    ptn = Patient.query.get_or_404(patient_id)
    return render_template('diagnosis_detail.html', patient=ptn)

@bp_diagnoses.route('/delete/<int:patient_id>', methods=['POST'])
def delete(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    try:
        # Hapus semua gambar dan prediksi yang terkait
        for image in patient.images:
            # Hapus file fisik dari sistem
            if image.image_path and os.path.exists(image.image_path):
                os.remove(image.image_path)

            # Hapus prediksi terkait gambar
            Prediction.query.filter_by(image_id=image.id).delete()

        # Hapus gambar
        Image.query.filter_by(patient_id=patient.id).delete()

        # Hapus diagnosis
        Diagnosis.query.filter_by(patient_id=patient.id).delete()

        # Terakhir, hapus pasien
        db.session.delete(patient)
        db.session.commit()
        flash("✅ Data pasien berhasil dihapus.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Gagal menghapus pasien: {e}", "danger")

    return redirect(url_for('diagnoses.index'))
