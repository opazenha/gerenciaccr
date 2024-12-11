// Use existing baseUrl from auth.js if available, otherwise define it
if (typeof baseUrl === 'undefined') {
    var baseUrl = window.location.protocol === 'https:' ? 'https://sterling-jolly-sailfish.ngrok-free.app' : 'http://localhost:7770';
}

// Wrap classes in an IIFE to prevent duplicate declarations
(function() {
    // Only declare classes if they haven't been declared yet
    if (typeof window.MediaSearch === 'undefined') {
        window.MediaSearch = class {
            constructor() {
                this.form = document.getElementById('mediaSearchForm');
                this.results = document.getElementById('searchResults');
                this.mediaGrid = document.querySelector('.grid');
                this.initializeDatePickers();
                this.attachEventListeners();
            }

            initializeDatePickers() {
                // Ensure Portuguese localization is set
                if (flatpickr.l10ns.pt) {
                    flatpickr.setDefaults({ locale: flatpickr.l10ns.pt });
                }

                const commonConfig = {
                    dateFormat: 'Y-m-d',
                    theme: 'dark',
                    disableMobile: true,
                    allowInput: false,
                    clickOpens: true,
                    time_24hr: true
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
                
                if (!mediaItems || mediaItems.length === 0) {
                    this.mediaGrid.innerHTML = '<p>Nenhuma mídia encontrada.</p>';
                    return;
                }

                this.mediaGrid.innerHTML = '';
                mediaItems.forEach(media => {
                    const card = this.createMediaCard(media);
                    this.mediaGrid.appendChild(card);
                });
            }

            createMediaCard(media) {
                const card = document.createElement('div');
                card.className = 'media-card';
                
                let videoId = '';
                if (media.url) {
                    videoId = this.getYouTubeVideoId(media.url);
                }
                
                const thumbnail = videoId ? 
                    `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg` :
                    '/static/images/default-thumbnail.jpg';

                card.innerHTML = `
                    <div class="media-thumbnail">
                        <img src="${thumbnail}" alt="Thumbnail">
                    </div>
                    <div class="media-info">
                        <h3>${media.title || 'Sem título'}</h3>
                        ${media.description ? `<p>${media.description}</p>` : ''}
                        ${media.url ? `
                            <div class="media-url">
                                <a href="${media.url}" target="_blank" rel="noopener noreferrer">
                                    Ver no YouTube
                                    <i class="ph ph-arrow-square-out"></i>
                                </a>
                            </div>
                        ` : ''}
                        ${media.date ? `
                            <div class="media-date">
                                <i class="ph ph-calendar"></i>
                                ${new Date(media.date).toLocaleDateString('pt-BR')}
                            </div>
                        ` : ''}
                    </div>
                `;

                return card;
            }

            getYouTubeVideoId(url) {
                const match = url.match(/[?&]v=([^&]+)/);
                return match ? match[1] : '';
            }
        }
    }

    // Initialize MediaSearch when the template is loaded
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM Content Loaded - Media Search');
        const mediaSearchForm = document.getElementById('mediaSearchForm');
        
        console.log('Media Search Form found:', !!mediaSearchForm);

        if (mediaSearchForm) {
            console.log('Initializing MediaSearch');
            new MediaSearch();
        }
    });
})();