// Use existing baseUrl from auth.js if available, otherwise define it
if (typeof baseUrl === 'undefined') {
    var baseUrl = window.location.protocol === 'https:' ? 'https://sterling-jolly-sailfish.ngrok-free.app' : 'http://localhost:7770';
}

// Define PostsCreator in the global scope
window.PostsCreator = class PostsCreator {
    constructor() {
        console.log('PostsCreator constructor called');
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.form = document.getElementById('createPostsForm');
        this.results = document.getElementById('postsResults');
        this.postsContent = document.getElementById('postsContent');
        
        console.log('PostsCreator elements found:', {
            form: this.form,
            results: this.results,
            postsContent: this.postsContent
        });
    }

    attachEventListeners() {
        if (!this.form) {
            console.error('Form not found - cannot attach event listeners');
            return;
        }

        console.log('Attaching submit event listener to form');
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            console.log('Form submitted - handling submission');
            
            const userInput = this.form.querySelector('textarea[name="userInput"]').value.trim();
            if (!userInput) {
                alert('Por favor, forneça uma descrição do conteúdo.');
                return;
            }

            try {
                console.log('Creating posts with input:', userInput);
                // Show loading state
                this.results.classList.remove('hidden');
                this.postsContent.innerHTML = '<div class="loading-spinner">Gerando posts...</div>';
                
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('No authentication token found');
                }

                const response = await fetch('/api/media/create_posts', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ request: userInput })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Server error:', {
                        status: response.status,
                        statusText: response.statusText,
                        errorText
                    });
                    throw new Error(`Server error: ${response.status} ${response.statusText}`);
                }

                const data = await response.json();
                console.log('Server response:', data);
                
                if (data.status === 'error') {
                    throw new Error(data.message || 'Unknown server error');
                }

                this.displayResults(data.posts);
            } catch (error) {
                console.error('Error creating posts:', error);
                this.postsContent.innerHTML = `<p class="error-message">Erro ao gerar posts: ${error.message}</p>`;
            }
        });
    }

    displayResults(posts) {
        if (!posts || posts.length === 0) {
            this.postsContent.innerHTML = '<p class="no-posts">Nenhum post foi gerado.</p>';
            return;
        }

        try {
            const formattedContent = posts.map(post => {
                try {
                    const lines = post.split('\n');
                    let formattedHtml = '<div class="post-container">';
                    
                    lines.forEach(line => {
                        const trimmedLine = line.trim();
                        if (trimmedLine.startsWith('#')) {
                            // Heading
                            formattedHtml += `<h2 class="post-heading">${trimmedLine.replace(/^#+\s*/, '')}</h2>`;
                        } else if (trimmedLine.startsWith('**')) {
                            // Bullet points
                            formattedHtml += `<div class="post-bullet">${trimmedLine.replace(/^\*\*/, '').replace(/\*\*$/, '')}</div>`;
                        } else if (trimmedLine.startsWith('Título do Post:') || trimmedLine.startsWith('Design do Post:')) {
                            // Section headers
                            formattedHtml += `<h3 class="post-section">${trimmedLine}</h3>`;
                        } else if (trimmedLine) {
                            // Regular paragraph
                            formattedHtml += `<p class="post-paragraph">${trimmedLine}</p>`;
                        }
                    });

                    formattedHtml += '</div>';

                    // Add CSS styles for dark theme
                    const styles = `
                        <style>
                            .post-container {
                                background: #2a2a2a;
                                border: 1px solid #3a3a3a;
                                border-radius: 8px;
                                padding: 20px;
                                margin: 15px 0;
                                color: #e0e0e0;
                                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                            }
                            .post-heading {
                                color: #ffffff;
                                font-size: 1.5em;
                                border-bottom: 1px solid #3a3a3a;
                                padding-bottom: 10px;
                                margin-bottom: 15px;
                            }
                            .post-section {
                                color: #ffffff;
                                font-size: 1.2em;
                                margin: 15px 0 10px 0;
                            }
                            .post-bullet {
                                color: #e0e0e0;
                                margin: 8px 0;
                                padding-left: 20px;
                                position: relative;
                            }
                            .post-bullet:before {
                                content: "•";
                                position: absolute;
                                left: 0;
                                color: #666;
                            }
                            .post-paragraph {
                                color: #d0d0d0;
                                line-height: 1.6;
                                margin: 10px 0;
                            }
                            .no-posts {
                                color: #e0e0e0;
                                text-align: center;
                                padding: 20px;
                            }
                            .error-message {
                                color: #ff6b6b;
                                background: rgba(255, 107, 107, 0.1);
                                padding: 10px;
                                border-radius: 4px;
                                margin: 10px 0;
                            }
                            .loading-spinner {
                                color: #e0e0e0;
                                text-align: center;
                                padding: 20px;
                            }
                        </style>
                    `;

                    return styles + formattedHtml;
                } catch (error) {
                    console.error('Error formatting post:', error);
                    return `<div class="error-message">Erro ao formatar post: ${error.message}</div>`;
                }
            }).join('');

            this.postsContent.innerHTML = formattedContent;
        } catch (error) {
            console.error('Error displaying results:', error);
            this.postsContent.innerHTML = `<div class="error-message">Erro ao exibir resultados: ${error.message}</div>`;
        }
    }
}

// No need for immediate initialization - dashboard.js will handle it
console.log('PostsCreator class defined');
