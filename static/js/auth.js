const baseUrl = window.location.protocol === 'https:' ? 'https://sterling-jolly-sailfish.ngrok-free.app' : '';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    // Handle login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearMessages(loginForm);

        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        if (!email || !password) {
            showError(loginForm, 'Por favor, preencha todos os campos');
            return;
        }

        try {
            const response = await fetch(`${baseUrl}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ email, password }),
                credentials: 'include'
            });

            const data = await response.json();

            if (response.ok) {
                showSuccess(loginForm, 'Login realizado com sucesso!');
                localStorage.setItem('token', data.token);
                setTimeout(() => {
                    window.location.href = `${baseUrl}/static/dashboard.html`;
                }, 1500);
            } else {
                showError(loginForm, data.message || 'Erro ao fazer login');
            }
        } catch (error) {
            console.error('Error:', error);
            showError(loginForm, 'Erro ao conectar ao servidor');
        }
    });

    // Helper functions to show error and success messages
    function showError(form, message) {
        clearMessages(form);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        form.appendChild(errorDiv);
    }

    function showSuccess(form, message) {
        clearMessages(form);
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        form.appendChild(successDiv);
    }

    function clearMessages(form) {
        const messages = form.querySelectorAll('.error-message, .success-message');
        messages.forEach(msg => msg.remove());
    }
});