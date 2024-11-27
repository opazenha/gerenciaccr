class VideoProcessor {
    constructor() {
        this.form = document.getElementById('videoProcessForm');
        this.status = document.getElementById('processingStatus');
        this.results = document.getElementById('results');
        this.processingMessage = document.getElementById('processingMessage');
        this.attachEventListeners();
    }

    attachEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const url = document.getElementById('videoUrl').value;
        const option = document.querySelector('input[name="processingOption"]:checked').value;

        if (!url) {
            this.showError('Por favor, insira uma URL válida.');
            return;
        }

        // Validate YouTube URL
        if (!this.isValidYouTubeUrl(url)) {
            this.showError('Por favor, insira uma URL válida do YouTube.');
            return;
        }

        try {
            const response = await this.processVideo(url, option);
            
            // Hide any existing content
            if (this.results) this.results.style.display = 'none';
            if (this.status) this.status.style.display = 'none';
            if (this.form) this.form.style.display = 'none';
            
            // Show the processing message
            this.showProcessingMessage(response.message);
            
        } catch (error) {
            console.error('Error processing video:', error);
            this.showError('Erro ao processar o vídeo. Por favor, tente novamente.');
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
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ url, option })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    showProcessingMessage(message) {
        // Create message container if it doesn't exist
        if (!this.processingMessage) {
            this.processingMessage = document.createElement('div');
            this.processingMessage.id = 'processingMessage';
            this.processingMessage.className = 'processing-message';
            this.form.parentNode.insertBefore(this.processingMessage, this.form.nextSibling);
        }

        this.processingMessage.innerHTML = `
            <div class="alert alert-info">
                <p>${message}</p>
            </div>
        `;
        this.processingMessage.style.display = 'block';
    }

    showError(message) {
        if (!this.processingMessage) {
            this.processingMessage = document.createElement('div');
            this.processingMessage.id = 'processingMessage';
            this.processingMessage.className = 'processing-message';
            this.form.parentNode.insertBefore(this.processingMessage, this.form.nextSibling);
        }

        this.processingMessage.innerHTML = `
            <div class="alert alert-danger">
                <p>${message}</p>
            </div>
        `;
        this.processingMessage.style.display = 'block';
    }

    isValidYouTubeUrl(url) {
        // Regular expression to match YouTube URLs
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
    }
}

// Initialize video processor when the template is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('videoProcessForm')) {
        new VideoProcessor();
    }
});
