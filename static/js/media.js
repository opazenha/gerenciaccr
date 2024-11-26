class MediaSearch {
    constructor() {
        this.form = document.getElementById('mediaSearchForm');
        this.results = document.getElementById('searchResults');
        this.mediaGrid = document.querySelector('.results-grid');
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
        if (data.status !== 'success') {
            throw new Error(data.message || 'Error searching media');
        }

        return data.media_posts;
    }

    displayResults(mediaItems) {
        this.results.style.display = 'block';
        this.mediaGrid.innerHTML = '';

        if (!mediaItems || mediaItems.length === 0) {
            this.mediaGrid.innerHTML = '<p class="no-results">Nenhuma mídia encontrada.</p>';
            return;
        }

        mediaItems.forEach(post => {
            const mediaCard = this.createMediaCard(post);
            this.mediaGrid.appendChild(mediaCard);
        });
    }

    createMediaCard(media) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Get YouTube video ID from URL
        const videoId = this.getYouTubeVideoId(media.url);
        
        card.innerHTML = `
            <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" 
                 alt="Thumbnail" class="result-thumbnail">
            <div class="result-info">
                <div class="result-title">${media.title || 'Sem título'}</div>
                <div class="result-date">${media.created_at}</div>
                ${media.description ? `
                    <p class="result-summary">${media.description}</p>
                ` : ''}
            </div>
        `;

        return card;
    }

    getYouTubeVideoId(url) {
        if (!url) return '';
        
        const regex = /[?&]v=([^&#]*)/;
        const match = url.match(regex);
        return match ? match[1] : '';
    }
}

// Initialize media search when the template is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('mediaSearchForm')) {
        new MediaSearch();
    }
});