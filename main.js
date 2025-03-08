document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');

    // Signup Form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('signupUsername').value;
            const password = document.getElementById('signupPassword').value;
            const response = await fetch('/sign-up', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            document.getElementById('signupMessage').textContent = data.message;
            if (response.status === 201) {
                window.location.href = '/login';
            }
        });
    }

    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            document.getElementById('loginMessage').textContent = data.message;
            if (response.status === 200) {
                localStorage.setItem('token', data.token);
                window.location.href = '/';
            }
        });
    }

    // Load Categories
    const categoriesDiv = document.getElementById('categories');
    if (categoriesDiv && token) {
        fetch('/categories', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(response => response.json())
        .then(data => {
            if (data.categories) {
                data.categories.forEach(category => {
                    const div = document.createElement('div');
                    div.className = 'category';
                    div.textContent = category;
                    div.onclick = () => window.location.href = `/category-details/${category}`;
                    categoriesDiv.appendChild(div);
                });
            } else {
                window.location.href = '/login';
            }
        });
    } else if (categoriesDiv) {
        window.location.href = '/login';
    }

    // Logout
    const logoutButton = document.getElementById('logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/login';
        });
    }
});