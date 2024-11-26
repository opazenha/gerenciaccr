class InfantilSearch {
    constructor() {
        console.log('Initializing InfantilSearch');
        this.form = document.getElementById('infantilSearchForm');
        this.results = document.getElementById('searchResults');
        this.infantilGrid = document.querySelector('.results-grid');
        
        console.log('Form element:', this.form);
        console.log('Results element:', this.results);
        console.log('Grid element:', this.infantilGrid);
        
        this.initializeDatePickers();
        this.attachEventListeners();
    }

    initializeDatePickers() {
        console.log('Initializing date pickers');
        flatpickr.localize(flatpickr.l10ns.pt);
        const commonConfig = {
            dateFormat: 'Y-m-d',
            theme: 'light'
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

            return data.results;
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    displayResults(reports) {
        console.log('Displaying results:', reports);
        
        if (!this.infantilGrid) {
            console.error('infantilGrid element not found');
            return;
        }

        this.results.style.display = 'block';
        this.infantilGrid.innerHTML = '';

        if (!reports || reports.length === 0) {
            console.log('No results found');
            this.infantilGrid.innerHTML = '<p class="no-results">Nenhum relatório encontrado.</p>';
            return;
        }

        reports.forEach(report => {
            console.log('Creating card for report:', report);
            const card = this.createReportCard(report);
            this.infantilGrid.appendChild(card);
        });
    }

    createReportCard(report) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Get YouTube video ID from URL if available
        const videoId = report.url ? this.getYouTubeVideoId(report.url) : null;
        
        card.innerHTML = `
            ${videoId ? `
                <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" 
                     alt="Thumbnail" class="result-thumbnail">
            ` : ''}
            <div class="result-info">
                <div class="result-title">${report.title || 'Sem título'}</div>
                <div class="result-date">${report.created_at}</div>
                ${report.description ? `
                    <p class="result-summary">${report.description}</p>
                ` : ''}
            </div>
        `;

        return card;
    }

    formatMarkdown(text) {
        if (!text) return '';
        
        // Convert markdown bold to HTML
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to <br>
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    getYouTubeVideoId(url) {
        if (!url) return '';
        
        const regex = /[?&]v=([^&#]*)/;
        const match = url.match(regex);
        return match ? match[1] : '';
    }
}