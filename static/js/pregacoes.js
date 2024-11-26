class SermonSearch {
    constructor() {
        this.form = document.getElementById('sermonSearchForm');
        this.results = document.getElementById('searchResults');
        this.sermonsGrid = document.querySelector('.results-grid');
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
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const url = this.form.videoUrl.value;
        const startDate = this.form.startDate.value;
        const endDate = this.form.endDate.value;

        // Validation
        if (!url && (!startDate || !endDate)) {
            alert('Por favor, forneça a URL do vídeo OU um intervalo de datas.');
            return;
        }

        if ((startDate && !endDate) || (!startDate && endDate)) {
            alert('Por favor, forneça ambas as datas para busca por período.');
            return;
        }

        try {
            // Show loading state
            this.sermonsGrid.innerHTML = '<p class="loading">Buscando pregações...</p>';
            this.results.style.display = 'block';
            
            const results = await this.searchSermons(url, startDate, endDate);
            this.displayResults(results);
        } catch (error) {
            console.error('Error searching sermons:', error);
            this.sermonsGrid.innerHTML = '<p class="error-message">Erro ao buscar pregações. Por favor, tente novamente.</p>';
        }
    }

    async searchSermons(url, startDate, endDate) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        const response = await fetch('/api/sermons/search', {
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
            throw new Error(data.message || 'Error searching sermons');
        }

        return data.sermons;
    }

    displayResults(sermons) {
        this.results.style.display = 'block';
        this.sermonsGrid.innerHTML = '';

        if (!sermons || sermons.length === 0) {
            this.sermonsGrid.innerHTML = '<p class="no-results">Nenhuma pregação encontrada.</p>';
            return;
        }

        sermons.forEach(sermon => {
            const sermonCard = this.createSermonCard(sermon);
            this.sermonsGrid.appendChild(sermonCard);
        });
    }

    createSermonCard(sermon) {
        const card = document.createElement('div');
        card.className = 'result-card';

        // Get YouTube video ID from URL
        const videoId = this.getYouTubeVideoId(sermon.url);
        
        card.innerHTML = `
            <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" 
                 alt="Thumbnail" class="result-thumbnail">
            <div class="result-info">
                <div class="result-title">${sermon.title || 'Sem título'}</div>
                <div class="result-date">${sermon.created_at}</div>
                ${sermon.final_summary ? `
                    <p class="result-summary">${sermon.final_summary}</p>
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

// Initialize sermon search when the template is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('sermonSearchForm')) {
        new SermonSearch();
    }
});