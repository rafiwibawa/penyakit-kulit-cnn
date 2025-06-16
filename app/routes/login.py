from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime 
from app import db
from app.models import User 
from werkzeug.security import check_password_hash

bp_login = Blueprint('login', __name__) 
 
@bp_login.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': 
            email = request.form.get('email') 
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                user.last_login = datetime.utcnow()
                db.session.commit()
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_role'] = user.role
                print("✅ Login berhasil, session:", dict(session))
                return redirect(url_for('dashboard.index'))
            else:
                flash('Email atau password salah', 'danger')
 
    return render_template('login.html') 

@bp_login.route('/logout')
def logout():
    session.clear()
    flash("Anda telah logout.", "info")
    return redirect(url_for('login.login'))