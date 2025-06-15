from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import base64
import io
import os

app = Flask(__name__)

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
    data = request.get_json()

    if 'share1' not in data or 'share2' not in data:
        return jsonify({'valid': False, 'error': 'Missing shares'})

    try:
        # Decode base64 to image bytes
        share1_data = base64.b64decode(data['share1'])
        share2_data = base64.b64decode(data['share2'])

        # Open both images
        img1 = Image.open(io.BytesIO(share1_data)).convert('1')
        img2 = Image.open(io.BytesIO(share2_data)).convert('1')

        # Overlay (logical AND for black pixels)
        combined = Image.new('1', img1.size)
        pixels1 = np.array(img1)
        pixels2 = np.array(img2)
        combined_pixels = np.bitwise_and(pixels1, pixels2)
        black_ratio = np.sum(combined_pixels == 0) / combined_pixels.size

        # You can adjust threshold as needed
        if black_ratio > 0.5:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})
# --- Entry point for cloud deployment ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
