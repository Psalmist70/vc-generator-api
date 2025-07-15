# phishing_detection/predict_utils.py

import joblib
import numpy as np
from PIL import Image
import tensorflow as tf
import os

# --- Load Models (once on import) ---
KNN_MODEL_PATH = "phishing_detection/knn_phishing_model.joblib"
CNN_MODEL_PATH = "phishing_detection/phishing_cnn_model.h5"

# Ensure paths are valid
if not os.path.exists(KNN_MODEL_PATH):
    raise FileNotFoundError(f"KNN model not found at {KNN_MODEL_PATH}")
if not os.path.exists(CNN_MODEL_PATH):
    raise FileNotFoundError(f"CNN model not found at {CNN_MODEL_PATH}")

# Load models
knn_model = joblib.load(KNN_MODEL_PATH)
cnn_model = tf.keras.models.load_model(CNN_MODEL_PATH)

# --- KNN Prediction Function ---
def predict_with_knn(features: list) -> str:
    """
    Takes extracted 30-dimensional feature list and returns prediction.
    Returns: 'phishing' or 'legitimate'
    """
    if not isinstance(features, list) or len(features) != 30:
        raise ValueError("Expected a list of 30 numeric features.")
    
    prediction = knn_model.predict([features])
    return 'phishing' if prediction[0] == -1 else 'legitimate'

# --- CNN Prediction Function ---
def predict_with_cnn(image_path: str) -> str:
    """
    Takes the path to an image file (screenshot) and returns prediction.
    Returns: 'phishing' or 'legitimate'
    """
    try:
        img = Image.open(image_path).resize((224, 224)).convert("RGB")
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = cnn_model.predict(img_array)
        return 'phishing' if prediction[0][0] > 0.5 else 'legitimate'
    except Exception as e:
        raise RuntimeError(f"Error in CNN prediction: {str(e)}")
