const video = document.getElementById('video');
const detectButton = document.getElementById('detectEmotion');
const cameraDialog = document.getElementById('camera-dialog');
const closeDialog = document.getElementById('close-dialog');
const captureButton = document.getElementById('capture');
const movieList = document.getElementById('movie-list');

let detectedEmotion = ''; // Menyimpan emosi yang terdeteksi

// Menampilkan dialog untuk membuka kamera
detectButton.addEventListener("click", () => {
    cameraDialog.style.display = 'flex'; // Menampilkan dialog
    startVideo();
});

// Menutup dialog
closeDialog.addEventListener("click", () => {
    cameraDialog.style.display = 'none'; // Menyembunyikan dialog
    stopVideo();
});

// Menampilkan video dari kamera
function startVideo() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(err => console.error("Error accessing camera:", err));
}

// Menghentikan video
function stopVideo() {
    const stream = video.srcObject;
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
    }
}

// Fungsi untuk menangkap gambar dari area kotak frame dan mengirimkannya ke server
function capture() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Ukuran kotak frame
    const frameWidth = 150; // Harus sesuai dengan CSS
    const frameHeight = 150;
    const videoWidth = video.videoWidth;
    const videoHeight = video.videoHeight;

    // Hitung posisi frame di tengah video
    const frameX = (videoWidth - frameWidth) / 2;
    const frameY = (videoHeight - frameHeight) / 2;

    // Set ukuran canvas
    canvas.width = frameWidth;
    canvas.height = frameHeight;

    // Potong area frame dari video
    ctx.drawImage(video, frameX, frameY, frameWidth, frameHeight, 0, 0, frameWidth, frameHeight);

    // Kirim gambar ke server
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'image.jpg'); // Menambahkan gambar ke FormData

        fetch('http://localhost:5000/detect-emotion', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert('Detected emotion: ' + data.emotion);
            detectedEmotion = data.emotion; // Simpan emosi yang terdeteksi
            displayMovies(data.movies); // Tampilkan film yang direkomendasikan
        })
        .catch(error => console.error("Error sending image:", error));
    });
}

let currentPage = 1; // Halaman aktif
const maxPage = 1000; // TMDB mendukung hingga 1000 halaman

function fetchMovies(page = 1) {
    const url = `http://localhost:5000/recommend?page=${page}`;

    fetch(url)
        .then(response => response.json())
        .then(movies => {
            displayMovies(movies); // Tampilkan film
            updatePaginationButtons(); // Perbarui status tombol
        })
        .catch(error => console.error("Error fetching movies:", error));
}

function nextPage() {
    if (currentPage < maxPage) {
        currentPage++;
        fetchMovies(currentPage);
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        fetchMovies(currentPage);
    }
}

function updatePaginationButtons() {
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageIndicator = document.getElementById('pageIndicator');

    // Perbarui tombol berdasarkan halaman saat ini
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === maxPage;

    // Tampilkan nomor halaman
    pageIndicator.textContent = `Page ${currentPage}`;
}

// Fungsi untuk menampilkan rekomendasi film
function displayMovies(movies) {
    movieList.innerHTML = ''; // Bersihkan daftar sebelumnya

    movies.forEach(movie => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
        <a href="/details/${movie.id}">
            <img src="https://image.tmdb.org/t/p/w500/${movie.poster_path}" alt="${movie.title}" class = "poster-thumb" />
            <span>${movie.title}</span>
        </a>
        `;
        movieList.appendChild(listItem);
    });
}

