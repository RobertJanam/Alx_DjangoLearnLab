// Main JavaScript file for Django Blog

// Document Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeForms();
    initializeAlerts();
    initializePasswordStrength();
    initializeFormValidation();
    initializePasswordToggles();
});

// Initialize form enhancements
function initializeForms() {
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        // Add focus effects
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
}

// Initialize alert auto-dismiss and close buttons
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            dismissAlert(alert);
        }, 5000);

        // Add close button if not present
        if (!alert.querySelector('.alert-close')) {
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.className = 'alert-close';
            closeBtn.setAttribute('aria-label', 'Close');
            closeBtn.onclick = function() {
                dismissAlert(alert);
            };
            alert.appendChild(closeBtn);
        }
    });
}

// Dismiss alert with animation
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

// Initialize password strength meter
function initializePasswordStrength() {
    const passwordInput = document.getElementById('id_password1');
    if (passwordInput) {
        // Create strength meter container if it doesn't exist
        let strengthContainer = passwordInput.parentNode.querySelector('.password-strength');
        if (!strengthContainer) {
            strengthContainer = document.createElement('div');
            strengthContainer.className = 'password-strength';
            strengthContainer.innerHTML = '<div class="strength-bar"></div>';
            passwordInput.parentNode.appendChild(strengthContainer);
        }

        const strengthBar = strengthContainer.querySelector('.strength-bar');

        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);

            // Update strength bar
            strengthBar.className = 'strength-bar';
            if (strength === 'weak') {
                strengthBar.classList.add('weak');
            } else if (strength === 'medium') {
                strengthBar.classList.add('medium');
            } else if (strength === 'strong') {
                strengthBar.classList.add('strong');
            }

            // Add strength text
            let strengthText = passwordInput.parentNode.querySelector('.strength-text');
            if (!strengthText) {
                strengthText = document.createElement('small');
                strengthText.className = 'strength-text';
                passwordInput.parentNode.appendChild(strengthText);
            }

            if (password.length > 0) {
                strengthText.textContent = `Password strength: ${strength.charAt(0).toUpperCase() + strength.slice(1)}`;
                strengthText.style.color = strength === 'weak' ? '#dc3545' : strength === 'medium' ? '#ffc107' : '#28a745';
            } else {
                strengthText.textContent = '';
            }
        });
    }
}

// Calculate password strength
function calculatePasswordStrength(password) {
    if (!password) return '';

    let score = 0;

    // Length check
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 2;

    // Character variety checks
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^a-zA-Z0-9]/.test(password)) score += 1;

    // Determine strength
    if (score <= 2) return 'weak';
    if (score <= 4) return 'medium';
    return 'strong';
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                // Remove existing error messages
                removeFieldError(field);

                if (!field.value.trim()) {
                    isValid = false;
                    markFieldAsError(field, 'This field is required');
                } else {
                    // Field-specific validation
                    if (field.type === 'email' && !isValidEmail(field.value)) {
                        isValid = false;
                        markFieldAsError(field, 'Please enter a valid email address');
                    }

                    if (field.id === 'id_password2' && field.value) {
                        const password1 = document.getElementById('id_password1');
                        if (password1 && field.value !== password1.value) {
                            isValid = false;
                            markFieldAsError(field, 'Passwords do not match');
                        }
                    }

                    if (field.id === 'id_username' && field.value.length < 3) {
                        isValid = false;
                        markFieldAsError(field, 'Username must be at least 3 characters long');
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
                // Scroll to first error
                const firstError = form.querySelector('.field-error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    });
}

// Initialize password toggle buttons
function initializePasswordToggles() {
    const passwordFields = ['id_password', 'id_password1', 'id_password2'];

    passwordFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.parentNode.querySelector('.password-toggle')) {
            const toggleBtn = document.createElement('i');
            toggleBtn.className = 'fas fa-eye password-toggle';
            toggleBtn.setAttribute('data-toggle', fieldId);

            toggleBtn.onclick = function() {
                togglePasswordVisibility(fieldId);
            };

            field.parentNode.style.position = 'relative';
            field.style.paddingRight = '40px';
            field.parentNode.appendChild(toggleBtn);
        }
    });
}

// Toggle password visibility
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);

    // Toggle icon
    const toggleBtn = document.querySelector(`[data-toggle="${inputId}"]`);
    if (toggleBtn) {
        toggleBtn.classList.toggle('fa-eye');
        toggleBtn.classList.toggle('fa-eye-slash');
    }
}

// Email validation helper
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Mark field as having error
function markFieldAsError(field, message) {
    field.classList.add('field-error');

    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error-message';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Remove field error
function removeFieldError(field) {
    field.classList.remove('field-error');
    const existingError = field.parentNode.querySelector('.field-error-message');
    if (existingError) {
        existingError.remove();
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading state to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function(e) {
        if (this.type === 'submit' && this.form) {
            const isValid = this.form.checkValidity();
            if (isValid) {
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="loading"></span> Loading...';
                this.disabled = true;

                // Re-enable after form submission (if needed)
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 3000);
            }
        }
    });
});

// Add Font Awesome if not present
if (!document.querySelector('link[href*="font-awesome"]')) {
    const fontAwesome = document.createElement('link');
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
    document.head.appendChild(fontAwesome);
}