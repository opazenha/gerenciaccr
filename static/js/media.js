// Use existing baseUrl from auth.js if available, otherwise define it
if (typeof baseUrl === 'undefined') {
    var baseUrl = window.location.protocol === 'https:' ? 'https://sterling-jolly-sailfish.ngrok-free.app' : 'http://localhost:7770';
}

class MediaSearch {
    constructor() {
        this.form = document.getElementById('mediaSearchForm');
        this.results = document.getElementById('searchResults');
        this.mediaGrid = document.querySelector('.grid');
        this.initializeDatePickers();
        this.attachEventListeners();
    }

    initializeDatePickers() {
        flatpickr.localize(flatpickr.l10ns.pt);
        const commonConfig = {
            dateFormat: 'Y-m-d',
            theme: 'light'
        };
        
        flatpickr('#startDate', commonConfig);
        flatpickr('#endDate', commonConfig);
    }

    attachEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const url = this.form.mediaUrl.value;
        const startDate = this.form.startDate.value;
        const endDate = this.form.endDate.value;

        // Validation
        if (!url && (!startDate || !endDate)) {
            alert('Por favor, forneça a URL da mídia OU um intervalo de datas.');
            return;
        }

        if ((startDate && !endDate) || (!startDate && endDate)) {
            alert('Por favor, forneça ambas as datas para busca por período.');
            return;
        }

        try {
            // Show loading state
            this.mediaGrid.innerHTML = '<p class="loading">Buscando mídia...</p>';
            this.results.style.display = 'block';
            
            const results = await this.searchMedia(url, startDate, endDate);
            this.displayResults(results);
        } catch (error) {
            console.error('Error searching media:', error);
            this.mediaGrid.innerHTML = '<p class="error-message">Erro ao buscar mídia. Por favor, tente novamente.</p>';
        }
    }

    async searchMedia(url, startDate, endDate) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        const response = await fetch('/api/media/search', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, startDate, endDate })
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/';
            return;
        }

        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message || 'Error searching media reports');
        }

        return data.data;
    }

    displayResults(mediaItems) {
        console.log('Starting displayResults with:', mediaItems);
        
        // Make sure we have the elements
        if (!this.results || !this.mediaGrid) {
            console.error('Missing elements:', {
                results: this.results,
                mediaGrid: this.mediaGrid
            });
            return;
        }

        // Show the results container
        this.results.classList.remove('hidden');
        console.log('Removed hidden class from results');
        
        // Clear existing content
        this.mediaGrid.innerHTML = '';
        console.log('Cleared grid content');

        if (!mediaItems || mediaItems.length === 0) {
            console.log('No results to display');
            this.mediaGrid.innerHTML = '<p class="no-results">Nenhuma mídia encontrada.</p>';
            return;
        }

        console.log(`Creating ${mediaItems.length} cards`);
        mediaItems.forEach((post, index) => {
            console.log(`Creating card ${index + 1}/${mediaItems.length}:`, post);
            const mediaCard = this.createMediaCard(post);
            if (mediaCard) {
                this.mediaGrid.appendChild(mediaCard);
                console.log(`Added card ${index + 1} to grid`);
            } else {
                console.error(`Failed to create card for:`, post);
            }
        });
        
        console.log('Finished displaying results');
    }

    createMediaCard(media) {
        console.log('Creating card with media:', media);
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Get YouTube video ID from URL
        const videoId = this.getYouTubeVideoId(media.url);
        console.log('Video ID:', videoId);
        
        // Handle media_posts content
        let postsContent = '';
        if (Array.isArray(media.media_posts)) {
            postsContent = media.media_posts.map(post => {
                const text = typeof post === 'object' ? post.text : post;
                return `<p class="result-post">${text}</p>`;
            }).join('');
        } else if (typeof media.media_posts === 'string') {
            postsContent = `<p class="result-post">${media.media_posts}</p>`;
        }
        
        const formattedDate = new Date(media.created_at).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        card.innerHTML = `
            <div class="result-card-inner">
                <div class="result-thumbnail">
                    <a href="${media.url}" target="_blank">
                        <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" 
                             alt="Thumbnail" class="thumbnail-img">
                    </a>
                </div>
                <div class="result-info">
                    <div class="result-date">${formattedDate}</div>
                    <div class="result-content">
                        ${postsContent}
                    </div>
                    <a href="${media.url}" target="_blank" class="result-link">Ver no YouTube</a>
                </div>
            </div>
        `;
        
        return card;
    }

    getYouTubeVideoId(url) {
        if (!url) return '';
        const match = url.match(/[?&]v=([^&]+)/);
        return match ? match[1] : '';
    }
}

// Initialize media search when the template is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('mediaSearchForm')) {
        new MediaSearch();
    }
});