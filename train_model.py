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
        if features is not None and img.note is not None:
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

def test_image_modelv2():
    # Ambil semua gambar bertipe 'data_uji'
    images = Image.query.filter_by(tipe_data='data_uji').all()

    if not images:
        print("Tidak ada data uji ditemukan.")
        return

    # Load model dan label encoder dari file
    model_path = 'model/random_forest.pkl'
    encoder_path = 'model/label_encoder.pkl'

    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        print("Model belum dilatih.")
        return

    model = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

    # Ekstraksi fitur dan label ground-truth (asli)
    X_test, y_true = [], []

    for img in images:
        features = extract_features(img.image_path)
        # Pastikan fitur berhasil diekstrak dan label tersedia
        if features is not None and img.note is not None:
            X_test.append(features)
            y_true.append(img.note)

    if not X_test:
        print("Tidak ada fitur valid dari data uji.")
        return

    # Konversi data uji ke array NumPy
    X_test = np.array(X_test)

    # Encode label ground-truth (misal dari 'normal' ke 0)
    y_true_encoded = label_encoder.transform(y_true)

    # Prediksi label menggunakan model yang telah dilatih
    y_pred = model.predict(X_test)

    # Hitung akurasi:
    # Jumlah prediksi yang benar dibagi jumlah total data uji
    acc = accuracy_score(y_true_encoded, y_pred)

    # Hitung skor F1 (rata-rata tertimbang)
    f1 = f1_score(y_true_encoded, y_pred, average='weighted')

    # Ambil nama-nama kelas dari label encoder
    target_names = label_encoder.classes_
    labels = list(range(len(target_names)))

    # Buat laporan klasifikasi lengkap
    report = classification_report(
        y_true_encoded,
        y_pred,
        labels=labels,
        target_names=target_names,
        zero_division=0
    ) 
    
    # Kembalikan hasil evaluasi model
    return {
        "accuracy": f"{acc*100:.2f}%",  # Akurasi dalam persen
        "f1_score": f"{f1:.2f}",         # Skor F1
        "report": report                 # Laporan klasifikasi lengkap
    }

def test_image_modelv3():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    import joblib, os
    import numpy as np

    # ======== Ambil data dari database ========
    data_latih = Image.query.filter_by(tipe_data='data_latih').all()
    data_uji = Image.query.filter_by(tipe_data='data_uji').all()

    if not data_latih:
        print("❌ Tidak ada data latih ditemukan.")
        return {"error": "Tidak ada data latih ditemukan."}
    if not data_uji:
        print("❌ Tidak ada data uji ditemukan.")
        return {"error": "Tidak ada data uji ditemukan."}

    # ======== Ekstraksi fitur ========
    X_train, y_train, X_test, y_true = [], [], [], []

    for img in data_latih:
        features = extract_features(img.image_path)
        if features is not None and img.note is not None:
            X_train.append(features)
            y_train.append(img.note)

    for img in data_uji:
        features = extract_features(img.image_path)
        if features is not None and img.note is not None:
            X_test.append(features)
            y_true.append(img.note)

    if not X_train or not X_test:
        print("⚠️ Fitur data latih atau uji kosong.")
        return {"error": "Fitur data latih atau uji kosong."}

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # ======== Encode label ========
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_true_encoded = label_encoder.transform(y_true)

    # ======== Latih model Random Forest ========
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train_encoded)

    # ======== Simpan model & encoder ========
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/random_forest.pkl")
    joblib.dump(label_encoder, "model/label_encoder.pkl")

    # ======== Evaluasi pada data latih ========
    y_pred_train = model.predict(X_train)
    acc_train = accuracy_score(y_train_encoded, y_pred_train)
    f1_train = f1_score(y_train_encoded, y_pred_train, average='weighted')
    report_train = classification_report(
        y_train_encoded,
        y_pred_train,
        labels=list(range(len(label_encoder.classes_))),
        target_names=label_encoder.classes_,
        zero_division=0
    )

    # ======== Evaluasi pada data uji ========
    y_pred_test = model.predict(X_test)
    acc_test = accuracy_score(y_true_encoded, y_pred_test)
    f1_test = f1_score(y_true_encoded, y_pred_test, average='weighted')
    report_test = classification_report(
        y_true_encoded,
        y_pred_test,
        labels=list(range(len(label_encoder.classes_))),
        target_names=label_encoder.classes_,
        zero_division=0
    )

    print("✅ Model berhasil dilatih dan diuji.")
    print(f"Jumlah data latih: {len(X_train)}, data uji: {len(X_test)}")
    print(f"Akurasi latih: {acc_train:.4f}, Akurasi uji: {acc_test:.4f}")

    return {
        "jumlah_data": {
            "latih": len(X_train),
            "uji": len(X_test)
        },
        "train_result": {
            "accuracy": f"{acc_train * 100:.2f}%",
            "f1_score": f"{f1_train:.2f}",
            "report": report_train
        },
        "test_result": {
            "accuracy": f"{acc_test * 100:.2f}%",
            "f1_score": f"{f1_test:.2f}",
            "report": report_test
        }
    }
