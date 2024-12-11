// Use existing baseUrl from auth.js if available, otherwise define it
if (typeof baseUrl === 'undefined') {
    var baseUrl = window.location.protocol === 'https:' ? 'https://sterling-jolly-sailfish.ngrok-free.app' : 'http://localhost:7770';
}

class InfantilSearch {
    constructor() {
        console.log('Initializing InfantilSearch');
        this.form = document.getElementById('infantilSearchForm');
        this.results = document.getElementById('searchResults');
        this.infantilGrid = document.querySelector('.grid');
        
        console.log('Form element:', this.form);
        console.log('Results element:', this.results);
        console.log('Grid element:', this.infantilGrid);
        
        this.initializeDatePickers();
        this.attachEventListeners();
    }

    initializeDatePickers() {
        console.log('Initializing date pickers');
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
        console.log('Attaching event listeners');
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                console.log('Form submitted');
                this.handleSubmit(e);
            });
        } else {
            console.error('Form element not found');
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        console.log('Handling form submission');
        
        const url = this.form.infantilUrl.value;
        const startDate = this.form.startDate.value;
        const endDate = this.form.endDate.value;

        console.log('Form values:', { url, startDate, endDate });

        if (!url && (!startDate || !endDate)) {
            alert('Por favor, forneça a URL do vídeo OU um intervalo de datas.');
            return;
        }

        if ((startDate && !endDate) || (!startDate && endDate)) {
            alert('Por favor, forneça ambas as datas para busca por período.');
            return;
        }

        try {
            this.infantilGrid.innerHTML = '<p class="loading">Buscando relatórios...</p>';
            this.results.style.display = 'block';
            
            console.log('Searching infantil reports...');
            const results = await this.searchInfantil(url, startDate, endDate);
            console.log('Search results:', results);
            
            this.displayResults(results);
        } catch (error) {
            console.error('Error searching reports:', error);
            this.infantilGrid.innerHTML = '<p class="error-message">Erro ao buscar relatórios. Por favor, tente novamente.</p>';
        }
    }

    async searchInfantil(url, startDate, endDate) {
        console.log('Making API request with:', { url, startDate, endDate });
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('No token found');
            window.location.href = '/';
            return;
        }

        try {
            const response = await fetch('/api/infantil/search', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, startDate, endDate })
            });

            console.log('API response status:', response.status);
            
            if (response.status === 401) {
                console.error('Unauthorized');
                localStorage.removeItem('token');
                window.location.href = '/';
                return;
            }

            const data = await response.json();
            console.log('API response data:', data);
            
            if (data.status === 'error') {
                throw new Error(data.message || 'Error searching infantil reports');
            }

            return data.data;
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    displayResults(infantilItems) {
        console.log('Starting displayResults with:', infantilItems);
        
        // Make sure we have the elements
        if (!this.results || !this.infantilGrid) {
            console.error('Missing elements:', {
                results: this.results,
                infantilGrid: this.infantilGrid
            });
            return;
        }

        // Show the results container
        this.results.classList.remove('hidden');
        console.log('Removed hidden class from results');
        
        // Clear existing content
        this.infantilGrid.innerHTML = '';
        console.log('Cleared grid content');

        if (!infantilItems || infantilItems.length === 0) {
            console.log('No results to display');
            this.infantilGrid.innerHTML = '<p class="no-results">Nenhum conteúdo infantil encontrado.</p>';
            return;
        }

        console.log(`Creating ${infantilItems.length} cards`);
        infantilItems.forEach((post, index) => {
            console.log(`Creating card ${index + 1}/${infantilItems.length}:`, post);
            const infantilCard = this.createReportCard(post);
            if (infantilCard) {
                this.infantilGrid.appendChild(infantilCard);
                console.log(`Added card ${index + 1} to grid`);
            } else {
                console.error(`Failed to create card for:`, post);
            }
        });
        
        console.log('Finished displaying results');
    }

    createReportCard(report) {
        console.log('Creating report card:', report);
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Get YouTube video ID from URL if available
        const videoId = report.url ? this.getYouTubeVideoId(report.url) : null;
        
        // Format the kids_report if available
        const formattedReport = report.kids_report ? this.formatMarkdown(report.kids_report) : '';
        
        const formattedDate = new Date(report.created_at).toLocaleDateString('pt-BR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        card.innerHTML = `
            <div class="result-card-inner">
                ${videoId ? `
                    <div class="result-thumbnail">
                        <a href="${report.url}" target="_blank">
                            <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" 
                                 alt="Thumbnail" class="thumbnail-img">
                        </a>
                    </div>
                ` : ''}
                <div class="result-info">
                    <div class="result-date">${formattedDate}</div>
                    <div class="result-content">
                        ${formattedReport}
                    </div>
                    ${report.url ? `
                        <a href="${report.url}" target="_blank" class="result-link">Ver no YouTube</a>
                    ` : ''}
                </div>
            </div>
        `;

        return card;
    }

    formatMarkdown(text) {
        if (!text) return '';
        
        // Convert markdown bold to HTML
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert markdown headers
        text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        text = text.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        
        // Convert line breaks to <br> and paragraphs
        text = text.split('\n\n').map(paragraph => 
            `<p>${paragraph.replace(/\n/g, '<br>')}</p>`
        ).join('');
        
        return text;
    }

    getYouTubeVideoId(url) {
        if (!url) return '';
        
        const regex = /[?&]v=([^&#]*)/;
        const match = url.match(regex);
        return match ? match[1] : '';
    }
}