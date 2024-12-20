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
emotion_model = tf.keras.models.load_model('emotion_models.h5')
emotion_labels = ['Angry', 'Disgusted', 'Fearful', 'Happy', 'Sad', 'Surprised', 'Neutral']

TMDB_API_KEY = '4822c132c84e58653f0d6ac31a477b69'

GENRE_MAP = {
    28: 'Action',
    12: 'Adventure',
    16: 'Animation',
    35: 'Comedy',
    80: 'Crime',
    99: 'Documentary',
    18: 'Drama',
    10751: 'Family',
    14: 'Fantasy',
    36: 'History',
    27: 'Horror',
    10402: 'Music',
    9648: 'Mystery',
    10749: 'Romance',
    878: 'Science Fiction',
    10770: 'TV Movie',
    53: 'Thriller',
    10752: 'War',
    37: 'Western'
}

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
        emotions = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']
        detected_emotion = emotions[emotion_index]

        # Mapping emosi ke genre TMDB
        emotion_to_genre = {
            'angry': 9648,     #Action
            'happy': 14,        #fantasy
            'sad': 35,           #Comedy
            'fearful': 53,        #Thriller
            'surprised': 12,     #Horor
            'disgusted': 35,    #Comedy
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
        return jsonify({'emotion': detected_emotion, 'movies': recommended_movies, 'genre_id' : genre_id })

    except Exception as e:
        print("Error during processing:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['GET'])
def recommend_movies():
    genre = request.args.get('genre', 'random')  # Genre or 'random'
    page = request.args.get('page', 1)  # Nomor halaman (default ke 1)
    query = f"&with_genres={genre}" if genre != 'random' else ""

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US{query}&sort_by=popularity.desc&page={page}"
    response = requests.get(url).json()

    return jsonify(response['results'])

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    page = request.args.get('page', 1)  # Nomor halaman (default ke 1)
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&page={page}&language=en-US"
    response = requests.get(url).json()

    return jsonify({
        'results': response.get('results', []),
        'page': response.get('page', 1),
        'total_pages': response.get('total_pages', 1)
    })



@app.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://www.youtube.com; "
        "frame-src https://www.youtube.com; "
        "style-src 'self' 'unsafe-inline'; "
    )
    return response

@app.route('/details/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    try:
        # Mendapatkan detail film
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        movie_response = requests.get(url).json()

        # Pastikan film ditemukan
        if movie_response.get('status_code') == 34:  # Film tidak ditemukan
            return jsonify({'error': 'Movie not found'}), 404

        # Mendapatkan trailer film
        trailer_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US"
        trailer_response = requests.get(trailer_url).json()
        trailer_id = None
        if 'results' in trailer_response and len(trailer_response['results']) > 0:
            trailer_id = trailer_response['results'][0]['key']  # Mengambil trailer pertama

        # Mendapatkan review pengguna
        reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}&language=en-US"
        reviews_response = requests.get(reviews_url).json()
        reviews = reviews_response.get('results', [])

        genre_names = []
        if 'genres' in movie_response:
            genre_names = [GENRE_MAP.get(genre['id'], 'Unknown') for genre in movie_response['genres']]

        # Menambahkan trailer_id, reviews, dan genre_names ke data movie
        movie_response['trailer_id'] = trailer_id
        movie_response['reviews'] = reviews
        movie_response['genres'] = genre_names

        return jsonify(movie_response)
    
    except Exception as e:
        print("Error fetching movie details:", str(e))
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch movie details'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
