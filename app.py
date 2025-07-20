from flask import Flask, request, jsonify
from flask_cors import CORS
from phishing_detection.predict_utils import predict_with_knn, predict_with_cnn
from phishing_detection.feature_extractor import extract_features
from PIL import Image
import numpy as np
import base64
import io
import os

app = Flask(__name__)
CORS(app)  # Allow external PHP/JS to call this API
# --- Utility functions ---
def create_vc_shares(image):
    image = image.convert('1')  # Convert to black and white
    pixels = np.array(image)
    height, width = pixels.shape

    share1 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    share2 = np.zeros((height * 2, width * 2), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            pixel = pixels[y, x]
            pattern = np.random.randint(0, 2)
            if pixel == 0:  # black pixel
                if pattern == 0:
                    s1 = np.array([[1, 0], [0, 1]])
                    s2 = np.array([[0, 1], [1, 0]])
                else:
                    s1 = np.array([[0, 1], [1, 0]])
                    s2 = np.array([[1, 0], [0, 1]])
            else:  # white pixel
                if pattern == 0:
                    s1 = s2 = np.array([[1, 0], [0, 1]])
                else:
                    s1 = s2 = np.array([[0, 1], [1, 0]])

            share1[y*2:y*2+2, x*2:x*2+2] = s1 * 255
            share2[y*2:y*2+2, x*2:x*2+2] = s2 * 255

    return Image.fromarray(share1), Image.fromarray(share2)

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- Routes ---
@app.route('/generate-vc-shares', methods=['POST'])
def generate_shares():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    try:
        image = Image.open(file.stream)
    except Exception as e:
        return jsonify({'error': 'Invalid image format'}), 400

    share1, share2 = create_vc_shares(image)
    return jsonify({
        'share1': image_to_base64(share1),
        'share2': image_to_base64(share2)
    })
@app.route('/validate-vc-shares', methods=['POST'])
def validate():
    try:
        data = request.get_json(force=True)  # Ensures JSON parsing

        share1_b64 = data.get('share1')
        share2_b64 = data.get('share2')

        if not share1_b64 or not share2_b64:
            return jsonify({'valid': False, 'error': 'Missing share1 or share2'}), 400

        # Decode base64
        share1_data = base64.b64decode(share1_b64)
        share2_data = base64.b64decode(share2_b64)

        # Convert to images
        img1 = Image.open(io.BytesIO(share1_data)).convert('1')
        img2 = Image.open(io.BytesIO(share2_data)).convert('1')

        # Ensure images are same size
        if img1.size != img2.size:
            return jsonify({'valid': False, 'error': 'Image sizes do not match'}), 400

        # Convert to numpy arrays
        pixels1 = np.array(img1)
        pixels2 = np.array(img2)

        # Bitwise AND
        combined_pixels = np.bitwise_and(pixels1, pixels2)

        # Count black pixels
        black_ratio = np.sum(combined_pixels == 0) / combined_pixels.size

        # Validate based on threshold
        if black_ratio > 0.5:
            return jsonify({'valid': True, 'black_pixel_ratio': round(black_ratio, 2)})
        else:
            return jsonify({'valid': False, 'black_pixel_ratio': round(black_ratio, 2)})

    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route("/predict-knn", methods=["POST"])
def knn_predict():
    data = request.get_json(force=True)
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Extract features from URL using feature_extractor
        features = extract_features(url)  # returns list or array

        # Predict using KNN
        knn_result = predict_with_knn(features)

        return jsonify({"prediction": knn_result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/predict-cnn", methods=["POST"])
def cnn_predict():
    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image = request.files["image"]
    path = "temp_image.jpg"
    image.save(path)

    try:
        result = predict_with_cnn(path)
        return jsonify({"prediction": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.route("/predict-combined", methods=["POST"])
def predict_combined():
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Step 1: Extract features from URL
        print("Step 1: extracting features...")
        from phishing_detection.feature_extractor import extract_features
        features = extract_features(url)

        # Step 2: Capture screenshot
        print("Step 2: taking screenshot...")
        from phishing_detection.screenshot_util import take_screenshot
        screenshot_path = take_screenshot(url)
        print(f"Screenshot saved to: {screenshot_path}")

        # Step 3: Predict using KNN and CNN
        print("Step 3: predicting...")
        from phishing_detection.predict_utils import predict_with_knn, predict_with_cnn
        knn_result = predict_with_knn(features)
        cnn_result = predict_with_cnn(screenshot_path)

        # Optional: Remove screenshot to free up memory
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        return jsonify({
            "knn_prediction": knn_result,
            "cnn_prediction": cnn_result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # Log full stack trace
        return jsonify({"error": str(e)}), 500

# --- Entry point for cloud deployment ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
