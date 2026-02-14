// Authentication specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeAuthForms();
    initializeAuthAlerts();
    initializePasswordToggle();
    initializeLoginValidation();
    initializeRegisterValidation();
});

function initializeAuthForms() {
    const authForms = document.querySelectorAll('.auth-form');
    authForms.forEach(form => {
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            // Add floating label effect
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });

            // Check initial state
            if (input.value) {
                input.parentElement.classList.add('focused');
            }
        });
    });
}

function initializeAuthAlerts() {
    const alerts = document.querySelectorAll('.auth-alert');
    alerts.forEach(alert => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            dismissAlert(alert);
        }, 5000);
    });
}

function dismissAlert(alert) {
    alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 500);
}

function initializePasswordToggle() {
    const passwordFields = ['id_password', 'id_password1', 'id_password2'];

    passwordFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.parentNode.querySelector('.password-toggle')) {
            const toggleBtn = document.createElement('i');
            toggleBtn.className = 'fas fa-eye password-toggle';
            toggleBtn.setAttribute('data-toggle', fieldId);
            toggleBtn.style.position = 'absolute';
            toggleBtn.style.right = '15px';
            toggleBtn.style.top = '50%';
            toggleBtn.style.transform = 'translateY(-50%)';
            toggleBtn.style.cursor = 'pointer';
            toggleBtn.style.color = '#667eea';
            toggleBtn.style.zIndex = '10';

            toggleBtn.onclick = function() {
                const input = document.getElementById(fieldId);
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
            };

            field.parentNode.style.position = 'relative';
            field.style.paddingRight = '40px';
            field.parentNode.appendChild(toggleBtn);
        }
    });
}

function initializeLoginValidation() {
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username');
            const password = document.getElementById('password');
            let isValid = true;

            // Remove existing errors
            removeErrors(loginForm);

            if (!username.value.trim()) {
                showError(username, 'Username is required');
                isValid = false;
            }

            if (!password.value) {
                showError(password, 'Password is required');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }
}

function initializeRegisterValidation() {
    const registerForm = document.querySelector('.register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const username = document.getElementById('id_username');
            const email = document.getElementById('id_email');
            const password1 = document.getElementById('id_password1');
            const password2 = document.getElementById('id_password2');
            let isValid = true;

            // Remove existing errors
            removeErrors(registerForm);

            // Username validation
            if (!username.value.trim()) {
                showError(username, 'Username is required');
                isValid = false;
            } else if (username.value.length < 3) {
                showError(username, 'Username must be at least 3 characters');
                isValid = false;
            } else if (!/^[a-zA-Z0-9_]+$/.test(username.value)) {
                showError(username, 'Username can only contain letters, numbers, and underscores');
                isValid = false;
            }

            // Email validation
            if (!email.value.trim()) {
                showError(email, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }

            // Password validation
            if (!password1.value) {
                showError(password1, 'Password is required');
                isValid = false;
            } else if (password1.value.length < 8) {
                showError(password1, 'Password must be at least 8 characters');
                isValid = false;
            }

            // Confirm password validation
            if (!password2.value) {
                showError(password2, 'Please confirm your password');
                isValid = false;
            } else if (password2.value !== password1.value) {
                showError(password2, 'Passwords do not match');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Add password strength indicator
        const password1 = document.getElementById('id_password1');
        if (password1) {
            password1.addEventListener('input', function() {
                updatePasswordStrength(this.value);
            });
        }
    }
}

function showError(field, message) {
    field.classList.add('error');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'auth-errorlist';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function removeErrors(form) {
    form.querySelectorAll('.error').forEach(field => {
        field.classList.remove('error');
    });

    form.querySelectorAll('.auth-errorlist').forEach(error => {
        error.remove();
    });
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function updatePasswordStrength(password) {
    let strengthContainer = document.getElementById('password-strength');
    if (!strengthContainer) {
        strengthContainer = document.createElement('div');
        strengthContainer.id = 'password-strength';
        strengthContainer.className = 'password-strength';
        strengthContainer.innerHTML = '<div class="strength-bar"></div>';
        document.getElementById('id_password1').parentNode.appendChild(strengthContainer);
    }

    const strengthBar = strengthContainer.querySelector('.strength-bar');
    const strength = calculatePasswordStrength(password);

    strengthBar.className = 'strength-bar';
    if (strength === 'weak') {
        strengthBar.classList.add('weak');
    } else if (strength === 'medium') {
        strengthBar.classList.add('medium');
    } else if (strength === 'strong') {
        strengthBar.classList.add('strong');
    }
}

function calculatePasswordStrength(password) {
    if (!password) return '';

    let score = 0;

    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^a-zA-Z0-9]/.test(password)) score += 1;

    if (score <= 2) return 'weak';
    if (score <= 4) return 'medium';
    return 'strong';
}