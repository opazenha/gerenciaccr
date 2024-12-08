document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    if (!localStorage.getItem('token')) {
        window.location.href = '/';
        return;
    }

    // Initialize sidebar functionality
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');
    const mainContent = document.getElementById('mainContent');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const contentArea = document.getElementById('contentArea');

    // Show welcome message and hide content area by default
    if (welcomeMessage && contentArea) {
        welcomeMessage.style.display = 'block';
        contentArea.style.display = 'none';
    }

    if (toggleBtn && sidebar && mainContent) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }

    // Handle navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', async (e) => {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(navItem => {
                if (navItem) navItem.classList.remove('active');
            });
            
            // Add active class to clicked item
            if (item) item.classList.add('active');

            // Get template path from data attribute
            const templatePath = item.getAttribute('data-template');
            if (templatePath) {
                await loadTemplate(templatePath);
            }
        });
    });

    async function loadTemplate(templatePath) {
        try {
            const response = await fetch(templatePath);
            const html = await response.text();
            
            // Hide welcome message and show content area
            if (welcomeMessage && contentArea) {
                welcomeMessage.style.display = 'none';
                contentArea.style.display = 'block';
                contentArea.innerHTML = html;
            } else if (mainContent) {
                mainContent.innerHTML = html;
            }

            // Load required script based on template
            let scriptPath = null;
            if (templatePath.includes('reservas.html')) {
                scriptPath = '/static/js/reservas.js';
            } else if (templatePath.includes('video.html')) {
                scriptPath = '/static/js/video.js';
            } else if (templatePath.includes('pregacoes.html')) {
                scriptPath = '/static/js/pregacoes.js';
            } else if (templatePath.includes('media.html')) {
                scriptPath = '/static/js/media.js';
            } else if (templatePath.includes('infantil.html')) {
                scriptPath = '/static/js/infantil.js';
            }

            if (scriptPath) {
                // Remove any existing script
                const existingScript = document.querySelector(`script[src="${scriptPath}"]`);
                if (existingScript) {
                    existingScript.remove();
                }

                // Load and execute the new script
                const script = document.createElement('script');
                script.src = scriptPath;
                script.onload = () => {
                    // Initialize component after script is loaded
                    if (templatePath.includes('reservas.html')) {
                        new ReservationForm();
                    } else if (templatePath.includes('video.html')) {
                        new VideoProcessor();
                    } else if (templatePath.includes('pregacoes.html')) {
                        new SermonSearch();
                    } else if (templatePath.includes('media.html')) {
                        new MediaSearch();
                    } else if (templatePath.includes('infantil.html')) {
                        new InfantilSearch();
                    }
                };
                document.body.appendChild(script);
            }
        } catch (error) {
            console.error('Error loading template:', error);
            if (contentArea) {
                contentArea.innerHTML = '<p class="error">Error loading content</p>';
            } else if (mainContent) {
                mainContent.innerHTML = '<p class="error">Error loading content</p>';
            }
        }
    }

    // Handle logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/';
        });
    }
});
