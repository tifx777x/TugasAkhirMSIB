// Mendapatkan detail film dari API
fetch(`/details/${movie_id}`)
    .then(response => response.json())
    .then(data => {
        // Menampilkan trailer sebagai background
        const trailerId = data.trailer_id;
        const trailerIframe = document.createElement('iframe');
        trailerIframe.src = `https://www.youtube.com/embed/${trailerId}?autoplay=1&mute=1&loop=1&playlist=${trailerId}`;
        trailerIframe.setAttribute('width', '100%');
        trailerIframe.setAttribute('height', '500');
        trailerIframe.setAttribute('frameborder', '0');
        trailerIframe.setAttribute('allow', 'autoplay; encrypted-media');
        trailerIframe.setAttribute('allowfullscreen', '');
        document.querySelector('.trailer-background').appendChild(trailerIframe);

        // Menampilkan review
        const reviewsContainer = document.getElementById('user-reviews');
        data.reviews.forEach(review => {
            const reviewDiv = document.createElement('div');
            reviewDiv.classList.add('review');
            reviewDiv.innerHTML = `
                <p><strong>${review.author}</strong>: </p>
                <p>${review.content}</p>
            `;
            reviewsContainer.appendChild(reviewDiv);
        });

        // Menampilkan detail lainnya seperti title, poster, overview, dll.
        document.querySelector('.movie-title').textContent = data.title;
        document.querySelector('.movie-poster').src = `https://image.tmdb.org/t/p/w500${data.poster_path}`;
        document.querySelector('.movie-release-date').textContent = data.release_date;
        document.querySelector('.movie-rating').textContent = `${data.vote_average}/10`;
        document.querySelector('.movie-overview').textContent = data.overview;
    })
    .catch(error => console.error('Error fetching movie details:', error));
