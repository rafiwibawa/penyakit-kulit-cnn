from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app import db
from app.models import Image
from app.models import ModelLog
from flask import session

bp_uji = Blueprint('uji', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp_uji.route('/data-uji', methods=['GET', 'POST'])
def upload_uji():
    if request.method == 'POST':
        if 'images' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('images') 
        note = request.form.get('note', 'data_uji')
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
                    tipe_data='data_uji'
                )
                db.session.add(new_image)
                saved_count += 1

        if saved_count > 0:
            db.session.commit()
            flash(f'{saved_count} file(s) successfully uploaded and saved.')
        else:
            flash('No valid files were uploaded.')

        return redirect(url_for('uji.upload_uji'))

    images = Image.query.filter_by(tipe_data='data_uji').order_by(Image.upload_time.desc()).all() 
    print("[Upload Uji] Session in GET:", dict(session))
    return render_template('uji.html', images=images)

@bp_uji.route('/uji-model', methods=["GET", "POST"])
def test_model():
    from train_model import test_image_model
    hasil = test_image_model()  # misalnya return dict berisi 'accuracy', 'f1_score', 'report'
    
    # Potong report hanya baris pertama (atau sebagian kecil)
    short_report = "\n".join(hasil["report"].split("\n")[:5]) + "\n..."

    session['hasil_uji'] = {
        "accuracy": hasil["accuracy"],
        "f1_score": hasil["f1_score"],
        "report": short_report
    }
    
    print("[Set Session] session['hasil_uji']:", session['hasil_uji'])
    flash("Model berhasil diuji pada data uji.")
    return redirect(url_for('uji.upload_uji'))


@bp_uji.route('/delete-image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    # Hapus file dari sistem file
    if image.image_path and os.path.exists(image.image_path):
        os.remove(image.image_path)

    db.session.delete(image)
    db.session.commit()
    flash('Gambar berhasil dihapus.', 'success')
    return redirect(url_for('latih.upload_latih'))
