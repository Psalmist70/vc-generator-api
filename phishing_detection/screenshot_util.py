# phishing_detection/screenshot_util.py

import requests
import os
from datetime import datetime

API_KEY = "80JMRDA-TWQ4MTQ-HS568E2-DJCJ42B"
API_URL = "https://shot.screenshotapi.net/screenshot"

def take_screenshot(url, filename="cnn_temp.jpg"):
    params = {
        "token": API_KEY,
        "url": url,
        "output": "image",
        "file_type": "jpg",
        "full_page": "true",
    }

    response = requests.get(API_URL, params=params, stream=True)
    
    if response.status_code == 200:
        os.makedirs("temp", exist_ok=True)
        path = os.path.join("temp", filename)
        
        with open(path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        return path
    else:
        raise Exception(f"Screenshot API failed with status code {response.status_code}")
