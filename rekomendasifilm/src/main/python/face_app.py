from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import numpy as np
import tensorflow as tf
import requests
import traceback

app = Flask(__name__)

CORS(app, origins=['http://localhost:8080'])

#app.config['CORS_ORIGINS'] = ['https://localhost:8080'] 
#app.config['CORS_HEADERS'] = ['Content-Type']

# Load emotion detection model
emotion_model = tf.keras.models.load_model('emotion_model.h5')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

TMDB_API_KEY = '4822c132c84e58653f0d6ac31a477b69'

@app.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Membaca gambar
        img = Image.open(file)
        img = img.convert('RGB')
        img_resized = img.resize((48, 48))
        img_array = np.array(img_resized)
        img_array = img_array.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Prediksi emosi
        prediction = emotion_model.predict(img_array)
        emotion_index = np.argmax(prediction)
        emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        detected_emotion = emotions[emotion_index]

        # Mapping emosi ke genre TMDB
        emotion_to_genre = {
            'angry': 28,       # Action
            'happy': 14,    # Romance
            'sad': 35,         # Comedy
            'fear': 53,        # Thriller
            'surprise': 27,
            'disgust': 35,
            'neutral': None,   # Semua Genre
        }
        genre_id = emotion_to_genre.get(detected_emotion)

        # Ambil rekomendasi dari TMDB
        if genre_id:
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
        else:
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&sort_by=popularity.desc"

        response = requests.get(url).json()
        recommended_movies = response['results']

        # Mengembalikan emosi dan rekomendasi film
        return jsonify({'emotion': detected_emotion, 'movies': recommended_movies})

    except Exception as e:
        print("Error during processing:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['GET'])
def recommend_movies():
    genre = request.args.get('genre', 'random')  # Genre or 'random'
    query = f"&with_genres={genre}" if genre != 'random' else ""

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US{query}&sort_by=popularity.desc"
    response = requests.get(url).json()

    return jsonify(response['results'])

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-US"
    response = requests.get(url).json()

    return jsonify(response['results'])

@app.route('/details/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
