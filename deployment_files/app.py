import os
import numpy as np
import cv2
import pydicom
import tensorflow as tf
from flask import Flask, request, jsonify
from PIL import Image
import io
import pandas as pd

app = Flask(__name__)

# Load the trained model
model = tf.keras.models.load_model('best_model.keras', custom_objects={'BinaryFocalCrossentropy': tf.keras.losses.BinaryFocalCrossentropy})

# Read model information from CSV and get the operating threshold
model_info = pd.read_csv('model_info.csv', header=None, index_col=0).squeeze("columns")
operating_threshold = float(model_info['Operating Threshold'])
print(f"Operating threshold: {operating_threshold}")

def preprocess_image(image_bytes, target_size=(192, 192)):
    # Try to read as DICOM first
    try:
        dicom_ds = pydicom.dcmread(io.BytesIO(image_bytes))
        img_array = dicom_ds.pixel_array.astype(np.float32)

        bits_stored = int(getattr(dicom_ds, "BitsStored", 16))
        img_array = img_array / ((2 ** bits_stored) - 1)

        if getattr(dicom_ds, "PhotometricInterpretation", "") == "MONOCHROME1":
            img_array = 1.0 - img_array

    except Exception:
        # If not DICOM, try common image formats (PNG, JPEG)
        img = Image.open(io.BytesIO(image_bytes)).convert('L') # Convert to grayscale
        img_array = np.array(img).astype(np.float32) / 255.0

    # Resize image
    img_resized = cv2.resize(img_array, target_size, interpolation=cv2.INTER_LINEAR)

    # Ensure 3 channels for model input
    if img_resized.ndim == 2:
        img_processed = np.stack([img_resized, img_resized, img_resized], axis=-1)
    else:
        img_processed = img_resized

    # Add batch dimension
    return np.expand_dims(img_processed, axis=0)

@app.route('/')
def home():
    return "Welcome to the Pneumonia Detection API!"

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        image_bytes = file.read()
        try:
            processed_image = preprocess_image(image_bytes)
            prediction = model.predict(processed_image)[0][0]
            result = 'Pneumonia' if prediction >= operating_threshold else 'No Pneumonia'
            confidence = round(float(prediction) * 100, 2)
            return jsonify({'Prediction': result, 'Confidence (%)': confidence})
        except Exception as e:
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)