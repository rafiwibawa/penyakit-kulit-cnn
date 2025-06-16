from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models import db, User
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import session

bp_register = Blueprint('register', __name__) 

@bp_register.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        # Validasi kosong
        if not email or not password or not repeat_password:
            print("⚠️ Field kosong, flash dijalankan")
            flash('Semua field wajib diisi.', 'danger')
            return redirect(url_for('register.register'))

        # Validasi password match
        if password != repeat_password:
            print("⚠️ Password tidak cocok")
            flash('Password dan ulangi password tidak cocok.', 'danger')
            return redirect(url_for('register.register'))

        # Cek apakah user sudah ada
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("⚠️ Email sudah terdaftar.")
            flash('Email sudah terdaftar.', 'warning')
            return redirect(url_for('register.register'))

        # Simpan user baru
        new_user = User(
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256"),  # Enkripsi password
            role='doctor',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()

        print("✅ User berhasil didaftarkan")
        flash('Registrasi berhasil. Silakan login.', 'success')
        return redirect(url_for('login.login')) 
    
    # print("Session:", dict(session))
    return render_template('register.html')
