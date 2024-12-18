let currentPage = 1; // Halaman saat ini
let totalPages = 1000; // Total halaman hasil pencarian
let currentQuery = ''; // Menyimpan query pencarian

// Fungsi untuk mendapatkan hasil pencarian
function fetchSearchResults(query, page = 1) {
    if (!query || query.trim() === '') {
        alert('Query cannot be empty!');
        return;
    }

    const url = `http://localhost:5000/search?query=${query}&page=${page}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Cek apakah data memiliki struktur yang diinginkan
            if (data && data.results && Array.isArray(data.results)) {
                displaySearchResults(data.results); // Menampilkan hasil pencarian
                totalPages = data.total_pages || 1; // Menyimpan total halaman
                updatePaginationButtons(); // Memperbarui tombol pagination
            } else {
                displayErrorMessage('Invalid search result format.');
            }
        })
        .catch(error => {
            console.error("Error fetching search results:", error);
            displayErrorMessage(error.message);
        });
}

// Fungsi untuk menampilkan hasil pencarian
function displaySearchResults(movies) {
    const movieList = document.getElementById('movie-list');
    movieList.innerHTML = ''; // Bersihkan hasil sebelumnya

    // Loop untuk menampilkan setiap film
    movies.forEach(movie => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            <a href="/details/${movie.id}">
                <img src="https://image.tmdb.org/t/p/w200/${movie.poster_path || 'default.jpg'}" alt="${movie.title}" class="poster-thumb" />
                <span>${movie.title}</span>
            </a>
        `;
        movieList.appendChild(listItem);
    });
}

// Fungsi untuk menampilkan pesan error
function displayErrorMessage(message) {
    const movieList = document.getElementById('movie-list');
    movieList.innerHTML = `<p>Error: ${message}</p>`;
}

// Fungsi untuk memperbarui tombol pagination
function updatePaginationButtons() {
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageIndicator = document.getElementById('pageIndicator');

    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === totalPages;
    pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
}

// Fungsi untuk berpindah ke halaman sebelumnya
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        fetchSearchResults(currentQuery, currentPage); // Ambil hasil untuk halaman sebelumnya
    }
}

// Fungsi untuk berpindah ke halaman berikutnya
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        fetchSearchResults(currentQuery, currentPage); // Ambil hasil untuk halaman selanjutnya
    }
}

// Ambil query dari URL dan tampilkan hasil pencarian pertama kali
window.onload = () => {
    const query = new URLSearchParams(window.location.search).get('query');
    if (query) {
        currentQuery = query; // Simpan query yang dipakai
        fetchSearchResults(query); // Tampilkan hasil pencarian pertama kali
    }
};
