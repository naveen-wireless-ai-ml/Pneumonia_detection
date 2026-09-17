import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Pneumonia Detection App", layout="centered")

st.title("Pneumonia Detection from Chest X-rays")
st.write("Upload a chest X-ray image to get a pneumonia prediction.")

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
</style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a DICOM (.dcm), PNG, or JPEG image...", type=["dcm", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption='Uploaded X-ray Image', use_column_width=True)
    st.write("")
    st.write("Classifying...")

    # Backend API URL - replace with your actual deployed backend URL if different
    backend_url = "https://special-acorn-r77p9q6q5vg9hp6gq-7860.app.github.dev/predict"

    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

    try:
        response = requests.post(backend_url, files=files)
        if response.status_code == 200:
            result = response.json()
            prediction_text = result.get("Prediction", "N/A")
            confidence = result.get("Confidence (%)", "N/A")

            st.markdown(
                f"""
                <div class="prediction-box">
                    <h3>Prediction: <span style='color: {'red' if prediction_text == 'Pneumonia' else 'green'};'>{prediction_text}</span></h3>
                    <p>Confidence: <strong>{confidence}%</strong></p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error(f"Error from backend: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend API. Please ensure the backend server is running and accessible.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.sidebar.header("About This App")
st.sidebar.info(
    "This application uses a deep learning model to analyze chest X-ray images"
    "and provide an indication of the likelihood of pneumonia. "
    "**Disclaimer:** The prediction is intended for informational and educational"
    "purposes only and should be considered an indicator, not a medical diagnosis."
    "Results should always be interpreted in conjunction with clinical findings and"
    "correlated with the observations and assessment of a qualified medical practitioner."
    "Do not use the prediction as a substitute for professional medical advice, diagnosis,"
    "or treatment."
)
