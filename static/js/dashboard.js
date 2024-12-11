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

            // Load required scripts based on template
            if (templatePath.includes('media.html')) {
                try {
                    // Remove existing scripts to ensure clean initialization
                    const existingScripts = document.querySelectorAll('script[src*="/static/js/"]');
                    existingScripts.forEach(script => script.remove());

                    // Load scripts in sequence and wait for them to be ready
                    await loadScript('/static/js/auth.js');
                    await loadScript('/static/js/media.js');
                    await loadScript('/static/js/create_post.js');
                    
                    // Initialize after ensuring scripts are loaded
                    const checkAndInitialize = () => {
                        if (typeof PostsCreator === 'undefined') {
                            console.log('Waiting for PostsCreator to be defined...');
                            setTimeout(checkAndInitialize, 100);
                        } else {
                            console.log('PostsCreator found, initializing...');
                            if (!window.postsCreator) {
                                window.postsCreator = new PostsCreator();
                            }
                        }
                    };
                    checkAndInitialize();
                } catch (error) {
                    console.error('Error initializing media scripts:', error);
                }
            } else if (templatePath.includes('reservas.html')) {
                await loadScript('/static/js/reservas.js');
                new ReservationForm();
            } else if (templatePath.includes('video.html')) {
                await loadScript('/static/js/video.js');
            } else if (templatePath.includes('pregacoes.html')) {
                await loadScript('/static/js/pregacoes.js');
            } else if (templatePath.includes('infantil.html')) {
                await loadScript('/static/js/infantil.js');
            }
        } catch (error) {
            console.error('Error loading template:', error);
            if (contentArea) {
                contentArea.innerHTML = '<p class="error">Error loading content. Please try again.</p>';
            }
        }
    }

    // Helper function to load scripts
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script is already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                console.log(`Script ${src} already loaded`);
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.onload = () => {
                console.log(`Script ${src} loaded successfully`);
                resolve();
            };
            script.onerror = (error) => {
                console.error(`Error loading script ${src}:`, error);
                reject(error);
            };
            document.body.appendChild(script);
        });
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
