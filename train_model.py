from app import db
from app.models import Image, ModelLog
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from datetime import datetime
import numpy as np
import joblib
import os
from utils.feature_extractor import extract_features
from sklearn.metrics import classification_report


def train_image_model():
    images = Image.query.filter_by(tipe_data='data_latih').all()

    X, y = [], []
    for img in images:
        features = extract_features(img.image_path)
        if features is not None:
            X.append(features)
            y.append(img.note)

    if not X:
        print("Tidak ada fitur yang berhasil diproses.")
        return

    X = np.array(X)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    os.makedirs('model', exist_ok=True)
    joblib.dump(model, 'model/random_forest.pkl')
    joblib.dump(le, 'model/label_encoder.pkl')

    log = ModelLog(
        model_name='MobileNet + RandomForest',
        trained_at=datetime.utcnow(),
        accuracy=acc,
        f1_score=f1,
        notes='Model dilatih dari data latih CNN',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    print(f'Model trained: Accuracy={acc:.2%}, F1={f1:.2f}')

def test_image_model():
    # Ambil semua gambar bertipe 'data_uji'
    images = Image.query.filter_by(tipe_data='data_uji').all()

    if not images:
        print("Tidak ada data uji ditemukan.")
        return

    # Load model dan label encoder
    model_path = 'model/random_forest.pkl'
    encoder_path = 'model/label_encoder.pkl'

    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        print("Model belum dilatih.")
        return

    model = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

    # Ekstraksi fitur dan label
    X_test, y_true = [], []

    for img in images:
        features = extract_features(img.image_path)
        if features is not None:
            X_test.append(features)
            y_true.append(img.note)

    if not X_test:
        print("Tidak ada fitur valid dari data uji.")
        return

   # Prediksi & Evaluasi
    X_test = np.array(X_test)
    y_true_encoded = label_encoder.transform(y_true)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_true_encoded, y_pred)
    f1 = f1_score(y_true_encoded, y_pred, average='weighted')

    target_names = label_encoder.classes_
    labels = list(range(len(target_names)))

    report = classification_report(
        y_true_encoded,
        y_pred,
        labels=labels,
        target_names=target_names,
        zero_division=0
    ) 
    
    return {
        "accuracy": f"{acc*100:.2f}%",
        "f1_score": f"{f1:.2f}",
        "report": report
    }

