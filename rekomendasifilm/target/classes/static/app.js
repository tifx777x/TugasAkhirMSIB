const video = document.getElementById('video');
const detectButton = document.getElementById('detectEmotion');
const cameraDialog = document.getElementById('camera-dialog');
const closeDialog = document.getElementById('close-dialog');

let currentPage = 1;  // Menyimpan halaman yang aktif
let detectedEmotion = ''; // Menyimpan emosi yang terdeteksi

// Menampilkan dialog untuk membuka kamera
detectButton.addEventListener("click", () => {
    cameraDialog.style.display = 'block'; // Menampilkan dialog
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

// Fungsi untuk menangkap gambar dan mengirimkannya ke server
// Fungsi untuk menangkap gambar dan mengirimkannya ke server
function capture() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Mengubah gambar menjadi RGB
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const imgArray = imgData.data;

    // Menambahkan RGB channel jika tidak ada
    for (let i = 0; i < imgArray.length; i += 4) {
        imgArray[i + 3] = 255; // Pastikan saluran alpha (transparansi) adalah 255 (tidak transparan)
    }

    // Menggambar ulang gambar RGB pada canvas
    ctx.putImageData(imgData, 0, 0);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'image.jpg'); // Menambahkan gambar ke FormData

        fetch('http://localhost:5000/detect-emotion', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {alert('Detected emotion: ' + data.emotion);
                            displayMovies(data.movies);
    })
            .catch(error => console.error("Error sending image:", error));
    });
}

function displayMovies(movies) {
    const movieList = document.getElementById('movie-list');
    movieList.innerHTML = ''; // Bersihkan daftar sebelumnya

    movies.forEach(movie => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            <img src="https://image.tmdb.org/t/p/w500/${movie.poster_path}" alt="${movie.title}" />
            <a href="/details/${movie.id}" target="_blank">${movie.title}</a>
        `;
        movieList.appendChild(listItem);
    });
}
