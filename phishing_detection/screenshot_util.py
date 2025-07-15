# phishing_detection/screenshot_util.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

def take_screenshot(url, filename="cnn_temp.jpg"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.set_window_size(1280, 800)
        driver.get(url)
        time.sleep(3)  # Allow time for full page load
        path = os.path.join("temp", filename)
        os.makedirs("temp", exist_ok=True)
        driver.save_screenshot(path)
        return path
    finally:
        driver.quit()
