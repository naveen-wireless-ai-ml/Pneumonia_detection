import streamlit as st
import requests
from PIL import Image
import io
import pydicom
import numpy as np

st.set_page_config(page_title="Pneumonia Prediction App", layout="centered")

st.markdown("""
<style>
h1 {
    font-size: 32px !important;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

st.title("Pneumonia Prediction from Chest X-rays")
st.write("Upload a chest X-ray image to get a pneumonia assessment.")

# Custom CSS for button styling
st.markdown("""
<style>
.stButton>button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 10px 0;
    cursor: pointer;
    border-radius: 8px;
    font-weight: bold;
    border: none;
}
.stButton>button:hover {
    background-color: #45a049;
}
.prediction-box {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
}
.disclaimer-box {
    background-color: #fff3cd;
    padding: 15px;
    border-radius: 8px;
    margin-top: 15px;
    border: 1px solid #ffeeba;
}
</style>
""", unsafe_allow_html=True)

# Main layout: 1/2 left and 1/2 right
left_col, image_col = st.columns([1, 1])
with left_col:
    uploaded_file = st.file_uploader(
        "Choose a DICOM (.dcm), PNG, or JPEG image...", type=["dcm", "png", "jpg", "jpeg"])
    predict_button = st.button("Predict", use_container_width=True)
    clear_button = st.button("Clear", use_container_width=True)

with image_col:
    if uploaded_file is not None:
        # Display uploaded image
        if uploaded_file.name.lower().endswith(".dcm"):
            try:
                dicom_ds = pydicom.dcmread(io.BytesIO(uploaded_file.getvalue()))
                img_array = dicom_ds.pixel_array.astype(np.float32)

                if getattr(dicom_ds, "PhotometricInterpretation", "") == "MONOCHROME1":
                    img_array = np.max(img_array) - img_array

                # Normalize for display
                img_min = np.min(img_array)
                img_max = np.max(img_array)

                if img_max > img_min:
                    img_array = ((img_array - img_min) / (img_max - img_min))

                st.image(img_array, caption="Uploaded X-ray Image", use_container_width=True)
            except Exception as e:
                st.error(f"Unable to display DICOM image: {e}")
        else:
            st.image(uploaded_file, caption="Uploaded X-ray Image", use_container_width=True)

if clear_button:
    st.rerun()

if predict_button:
    if uploaded_file is None:
        st.warning("Please upload a chest X-ray image first.")
    else:
        # Backend API URL
        backend_url = ("https://special-acorn-r77p9q6q5vg9hp6gq-7860.app.github.dev/predict")
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        with st.spinner("Analyzing X-ray..."):
            try:
                response = requests.post(backend_url, files=files)
                if response.status_code == 200:
                    result = response.json()

                    prediction_text = result.get("Prediction", "N/A")
                    confidence = result.get("Confidence (%)", "N/A")

                    if "No Pneumonia" in prediction_text:
                        display_text = ("No Pneumonia Detected")
                        text_color = "green"
                    else:
                        display_text = ("Findings suggestive of Pneumonia")
                        text_color = "red"

                    st.markdown(
                        f"""
                        <div class="prediction-box">
                            <h3>Assessment:
                                <span style='color: {text_color};'>
                                    {display_text}
                                </span>
                            </h3>
                            <p>Model Confidence:
                                <strong>{confidence}%</strong>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        """
                        <div class="disclaimer-box">
                            <strong>Disclaimer:</strong><br>
                            This prediction is intended for informational and
                            educational purposes only and is an indicator, not
                            a medical diagnosis. Results should be interpreted
                            in conjunction with clinical findings and correlated
                            with the observations and assessment of a qualified
                            medical practitioner. Do not use this prediction as
                            a substitute for professional medical advice,
                            diagnosis, or treatment.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:
                    st.error(f"Error from backend: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the backend API. Please ensure "
                    "the backend server is running and accessible."
                )

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.sidebar.header("About This App")
st.sidebar.info(
    "This application uses a deep learning model to analyze chest X-ray "
    "images and provide an indication of the likelihood of pneumonia."
)