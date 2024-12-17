import cv2
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from flask import Flask, jsonify
import threading

# Muat model deteksi ekspresi wajah
model = load_model('emotion_model.keras')  # Pastikan Anda memiliki model deteksi ekspresi wajah

# Muat dataset movies.csv untuk rekomendasi
movies_df = pd.read_csv('emotion_service/dataset/processed_movies.csv')

# Daftar ekspresi yang dapat dikenali
emotion_labels = ['Angry', 'Disguist', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Muat model deteksi wajah
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Fungsi untuk merekomendasikan film berdasarkan ekspresi
def recommend_movies(emotion):
    recommendations = {
        'Happy': ['Comedy', 'Romantic', 'Action'],
        'Sad': ['Comedy', 'Drama', 'Romantic'],
        'Angry': ['Action', 'Thriller', 'Comedy'],
        'Fear': ['Horror', 'Mystery','Fantasy'],
        'Surprise': ['Fantasy', 'Action', 'Thriller'],
        'Neutral': ['Adventure', 'Animation'],
        'Disguist': ['Horror', 'Thriller']
    }

    genres = recommendations.get(emotion, ['General'])
    recommended_movies = movies_df[movies_df['genres'].isin(genres)]
    return recommended_movies[['title', 'genres']].to_dict(orient='records')

# Flask Setup
app = Flask(__name__)

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion_from_face():
    # Capture image from webcam (or send image through API)
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return jsonify({"error": "Failed to capture image"}), 400

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        return jsonify({"error": "No face detected"}), 400

    # Ambil wajah pertama yang terdeteksi
    (x, y, w, h) = faces[0]
    face = frame[y:y + h, x:x + w]
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = cv2.resize(face, (48, 48))  # Mengubah ukuran sesuai model
    face = face / 255.0
    face = np.expand_dims(face, axis=0)

    # Prediksi ekspresi wajah
    emotion_prob = model.predict(face)
    max_index = np.argmax(emotion_prob[0])
    emotion = emotion_labels[max_index]

    # Mengambil rekomendasi film
    recommended_movies = recommend_movies(emotion)


    return jsonify({
        'emotion': emotion,
        'recommended_movies': recommended_movies
    })

# Fungsi untuk menjalankan Flask server di background
def run_flask():
    app.run(debug=True, use_reloader=False)

# Menjalankan Flask API di thread terpisah
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()