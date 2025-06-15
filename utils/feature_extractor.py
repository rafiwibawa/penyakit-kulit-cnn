from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input # type: ignore
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from skimage.feature import local_binary_pattern
from skimage.color import rgb2gray
from PIL import Image

mobilenet = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

def extract_features(image_path):
    try:
        #Fitur CNN
        # Diproses oleh arsitektur MobileNetV2.
        # Sudah belajar pola kompleks dari banyak gambar selama pretraining di ImageNet.
        # Termasuk bentuk, tekstur halus, tepi, warna global, dan pola kombinasi yang lebih abstrak.
        # Bukan nilai RGB mentah (misalnya img[100,100] = [255, 0, 0]).

        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        features = mobilenet.predict(img_array, verbose=0)
        return features[0]  # return shape (1280,)
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def extract_featuresV2(image_path):
    try:
        # Fitur CNN
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        cnn_features = mobilenet.predict(img_array, verbose=0)[0]  # shape (1280,)

        # Fitur LBP (tekstur)
        lbp_features = extract_lbp_features(image_path)  # shape (10,) by default

        if lbp_features is not None:
            # Gabungkan keduanya
            combined_features = np.concatenate([cnn_features, lbp_features])
            return combined_features
        else:
            return cnn_features  # fallback ke CNN saja

    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def extract_lbp_features(image_path, P=8, R=1):
    try:
        image = Image.open(image_path).resize((224, 224)).convert('RGB')
        gray_image = rgb2gray(np.array(image))
        lbp = local_binary_pattern(gray_image, P, R, method='uniform')
        
        # Buat histogram LBP
        (hist, _) = np.histogram(
            lbp.ravel(),
            bins=np.arange(0, P + 3),  # uniform pattern = P+2 bins
            range=(0, P + 2)
        )
        # Normalize histogram
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-7)
        return hist
    except Exception as e:
        print(f"Error reading LBP from {image_path}: {e}")
        return None
