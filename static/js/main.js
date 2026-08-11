// ====== LOGOUT ======
function logoutUser() {
    fetch('/logout/', {
        method: 'POST',
        headers: { 'Authorization': 'JWT ' + localStorage.getItem('token') }
    })
    .finally(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user');
        window.location.href = '/';
    });
}

// ====== CHECK LOGIN STATUS ======
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        // User is not logged in
        return false;
    }
    return true;
}

// ====== UPDATE NAVBAR ======
function updateNavbar() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (token && user.username) {
        // Show logged-in state
        document.querySelectorAll('.auth-required').forEach(el => el.style.display = 'block');
        document.querySelectorAll('.auth-guest').forEach(el => el.style.display = 'none');
        // Update welcome message
        const welcomeEl = document.querySelector('.welcome-message');
        if (welcomeEl) {
            welcomeEl.textContent = 'Welcome, ' + (user.first_name || user.username);
        }
    } else {
        // Show guest state
        document.querySelectorAll('.auth-required').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.auth-guest').forEach(el => el.style.display = 'block');
    }
}

// ====== INITIALIZE ON PAGE LOAD ======
document.addEventListener('DOMContentLoaded', function() {
    updateNavbar();
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});