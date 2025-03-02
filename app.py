from flask import Flask, request, render_template, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os
import io
import uuid
import gdown
from PIL import Image
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS for MERN frontend

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

MODEL_PATH = "PlantVillage.h5"
GOOGLE_DRIVE_ID = "1-HPmegh4ef3bUfbxjcsAEwxRPl4jFdMA"  # Your Google Drive File ID

# Download model if not available
if not os.path.exists(MODEL_PATH):
    print("Downloading model from Google Drive...")
    gdown.download(f"https://drive.google.com/uc?id={GOOGLE_DRIVE_ID}", MODEL_PATH, quiet=False)

# Load the trained model
model = tf.keras.models.load_model(MODEL_PATH)

class_info = {
    'Pepper__bell___Bacterial_spot': {'description': 'Bacterial spot is caused by Xanthomonas campestris.', 'precautions': 'Avoid overhead irrigation and use bactericides.'},
    'Pepper__bell___healthy': {'description': 'Healthy bell pepper plant.', 'precautions': 'Maintain good cultural practices.'},
    'Potato___Early_blight': {'description': 'Early blight caused by Alternaria solani.', 'precautions': 'Use fungicides and remove infected debris.'},
    'Potato___Late_blight': {'description': 'Late blight caused by Phytophthora infestans.', 'precautions': 'Apply fungicides and ensure drainage.'},
    'Potato___healthy': {'description': 'Healthy potato plant.', 'precautions': 'Monitor for pests.'},
    'Tomato_Bacterial_spot': {'description': 'Bacterial spot caused by Xanthomonas campestris.', 'precautions': 'Use resistant varieties.'},
    'Tomato_Early_blight': {'description': 'Early blight caused by Alternaria solani.', 'precautions': 'Use fungicides and remove infected plant material.'},
    'Tomato_Late_blight': {'description': 'Late blight caused by Phytophthora infestans.', 'precautions': 'Apply fungicides regularly and remove infected plants.'},
    'Tomato_healthy': {'description': 'Healthy tomato plant.', 'precautions': 'Maintain good cultural practices.'}
}

# Function to predict disease
def predict_disease(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    predicted_index = np.argmax(predictions)

    class_label = list(class_info.keys())[predicted_index]
    return class_label, class_info[class_label]

# 🏠 Serve HTML UI
@app.route('/')
def home():
    return render_template('index.html', prediction=None, details=None, img_path=None)

# 📸 Handle File Upload & Prediction
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error="No file uploaded")

    file = request.files['file']
    if file:
        filename = str(uuid.uuid4()) + "_" + file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        prediction, details = predict_disease(file_path)
        return render_template('index.html', prediction=prediction, details=details, img_path=file_path)

# 🎯 Handle Camera Upload
@app.route('/upload_camera', methods=['POST'])
def upload_camera():
    if 'file' not in request.files:
        return render_template('index.html', error="No file received from camera")

    file = request.files['file']
    if file:
        filename = "captured_" + str(uuid.uuid4()) + ".jpg"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        img = Image.open(io.BytesIO(file.read()))
        img.save(img_path)

        prediction, details = predict_disease(img_path)
        return render_template('index.html', prediction=prediction, details=details, img_path=img_path)

# 🏃‍♂️ Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    app.run(host='0.0.0.0', port=port)
