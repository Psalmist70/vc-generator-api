import joblib
import numpy as np
from PIL import Image
import tensorflow as tf

# Load KNN model
knn_model = joblib.load("phishing_detection/knn_phishing_model.joblib")

# Load CNN model
cnn_model = tf.keras.models.load_model("phishing_detection/phishing_cnn_model.h5")

def predict_with_knn(features: list):
    """Takes extracted feature list (e.g. from URL) and returns prediction"""
    prediction = knn_model.predict([features])
    return 'phishing' if prediction[0] == -1 else 'legitimate'

def predict_with_cnn(image_path):
    """Takes a screenshot or image file and returns CNN classification"""
    img = Image.open(image_path).resize((224, 224)).convert("RGB")
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = cnn_model.predict(img_array)
    return 'phishing' if prediction[0][0] > 0.5 else 'legitimate'
