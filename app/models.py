from . import db
from sqlalchemy.dialects.mysql import ENUM

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(ENUM('admin', 'doctor', 'staff'), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    gender = db.Column(ENUM('male', 'female'), nullable=False)
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_path = db.Column(db.String(255))
    upload_time = db.Column(db.DateTime)
    note = db.Column(db.Text)
    tipe_data = db.Column(db.String(20), nullable=False, default='data_latih')
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    model_version = db.Column(db.String(100))
    predicted_label = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    prediction_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    diagnosis = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class ModelLog(db.Model):
    __tablename__ = 'model_logs'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100))
    trained_at = db.Column(db.DateTime)
    accuracy = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
