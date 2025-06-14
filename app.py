from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import base64
import io

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    file = request.files['image']
    image = Image.open(file).convert('1')
    width, height = image.size
    share1 = Image.new('1', (width * 2, height * 2))
    share2 = Image.new('1', (width * 2, height * 2))
    pixels = image.load()
    s1_pixels = share1.load()
    s2_pixels = share2.load()
    import random
    for y in range(height):
        for x in range(width):
            pattern = random.choice([(0,1,1,0),(1,0,0,1)])
            s1 = pattern
            s2 = pattern[::-1]
            for dy in range(2):
                for dx in range(2):
                    s1_pixels[x*2+dx, y*2+dy] = s1[dy*2 + dx]
                    s2_pixels[x*2+dx, y*2+dy] = s2[dy*2 + dx]

    # Convert both to base64
    s1_buf = io.BytesIO()
    s2_buf = io.BytesIO()
    share1.save(s1_buf, format='PNG')
    share2.save(s2_buf, format='PNG')
    return jsonify({
        'share1': base64.b64encode(s1_buf.getvalue()).decode(),
        'share2': base64.b64encode(s2_buf.getvalue()).decode()
    })

if __name__ == '__main__':
    app.run(debug=True)
