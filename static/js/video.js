class VideoProcessor {
    constructor() {
        this.form = document.getElementById('videoProcessForm');
        this.status = document.getElementById('processingStatus');
        this.results = document.getElementById('results');
        this.attachEventListeners();
    }

    attachEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(button => {
            button.addEventListener('click', () => this.switchTab(button.dataset.tab));
        });
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(this.form);
        const url = formData.get('videoUrl');
        const option = formData.get('processingOption');

        if (!url) {
            alert('Por favor, insira a URL do vídeo.');
            return;
        }

        try {
            this.showProcessingStatus();
            const response = await this.processVideo(url, option);
            this.updateProgressSteps(option);
            this.displayResults(response);
        } catch (error) {
            console.error('Error processing video:', error);
            alert('Erro ao processar o vídeo. Por favor, tente novamente.');
        }
    }

    async processVideo(url, option) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        const response = await fetch('/api/video/process', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, option })
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/';
            return;
        }

        const data = await response.json();
        if (data.status !== 'success') {
            throw new Error(data.message || 'Error processing video');
        }

        return data;
    }

    showProcessingStatus() {
        this.form.style.display = 'none';
        this.status.style.display = 'block';
        this.results.style.display = 'none';
    }

    updateProgressSteps(option) {
        const steps = ['transcription', 'summary'];
        if (option === 'media' || option === 'completo') {
            steps.push('media');
        }
        if (option === 'completo') {
            steps.push('kids', 'groups');
        }

        steps.forEach((step, index) => {
            setTimeout(() => {
                const stepEl = document.querySelector(`[data-step="${step}"]`);
                stepEl.classList.add('completed');
            }, index * 1000);
        });
    }

    displayResults(data) {
        this.status.style.display = 'none';
        this.results.style.display = 'block';
        document.querySelector('.video-input-section').style.display = 'none';

        // Display summary
        if (data.final_summary) {
            const summaryParts = this.parseSummary(data.final_summary);
            document.getElementById('summaryText').textContent = summaryParts.summary;
            this.displayList('bibleReferences', summaryParts.references);
            this.displayList('mainPoints', summaryParts.points);
        }

        // Display media posts
        if (data.media_posts) {
            const postsContainer = document.querySelector('.post-templates');
            postsContainer.innerHTML = '';
            
            // Check if media_posts is a string, if so convert it to array of objects
            let posts = data.media_posts;
            if (typeof posts === 'string') {
                posts = posts.split('\n\n')
                    .filter(post => post.trim())
                    .map(post => ({ text: post.trim() }));
            }
            
            // Ensure posts is an array before using forEach
            if (Array.isArray(posts)) {
                posts.forEach(post => {
                    const postEl = this.createPostElement(post);
                    postsContainer.appendChild(postEl);
                });
            } else {
                console.error('media_posts is neither a string nor an array:', posts);
            }
        }

        // Display kids report
        if (data.kids_report) {
            document.getElementById('kidsContent').textContent = data.kids_report;
        }

        // Display groups report
        if (data.gc_report) {
            document.getElementById('groupsContent').textContent = data.gc_report;
        }

        // Show appropriate tabs based on available data
        this.updateAvailableTabs(data);

        const resultsContainer = document.getElementById('processingResults');
        resultsContainer.innerHTML = '';

        if (!data || Object.keys(data).length === 0) {
            resultsContainer.innerHTML = '<p class="no-results">Nenhum resultado encontrado.</p>';
            return;
        }

        const videoId = this.getYouTubeVideoId(data.url);
        const resultElement = document.createElement('div');
        resultElement.className = 'video-result-card';
        
        resultElement.innerHTML = `
            <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" 
                 alt="Thumbnail" class="video-thumbnail">
            <div class="video-info">
                <div class="video-title">${data.title || 'Sem título'}</div>
                <div class="video-date">${data.created_at}</div>
                <div class="video-status">Status: ${data.status}</div>
                ${data.error ? `<div class="video-error">Erro: ${data.error}</div>` : ''}
            </div>
        `;

        resultsContainer.appendChild(resultElement);
    }

    getYouTubeVideoId(url) {
        if (!url) return '';
        
        const regex = /[?&]v=([^&#]*)/;
        const match = url.match(regex);
        return match ? match[1] : '';
    }

    parseSummary(summary) {
        const parts = summary.split('Referências Bíblicas:');
        const mainParts = parts[0].split('Pontos Principais:');
        
        return {
            summary: mainParts[0].trim(),
            points: mainParts[1] ? mainParts[1].trim().split('\n').map(p => p.trim()) : [],
            references: parts[1] ? parts[1].trim().split('\n').map(r => r.trim()) : []
        };
    }

    displayList(elementId, items) {
        const ul = document.getElementById(elementId);
        ul.innerHTML = '';
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            ul.appendChild(li);
        });
    }

    createPostElement(post) {
        const div = document.createElement('div');
        div.className = 'post-template';
        div.innerHTML = `
            <div class="post-text">${post.text}</div>
            <div class="post-actions">
                <button class="btn-copy" onclick="navigator.clipboard.writeText('${post.text}')">
                    <i class="ph ph-copy"></i>
                    Copiar Texto
                </button>
            </div>
        `;
        return div;
    }

    updateAvailableTabs(data) {
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            const tabName = tab.dataset.tab;
            const hasData = (
                tabName === 'summary' && data.final_summary ||
                tabName === 'media' && data.media_posts ||
                tabName === 'kids' && data.kids_report ||
                tabName === 'groups' && data.gc_report
            );
            tab.style.display = hasData ? 'block' : 'none';
        });
    }

    switchTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update active tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabName}Tab`);
        });
    }
}

// Initialize video processor when the template is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('videoProcessForm')) {
        new VideoProcessor();
    }
});
