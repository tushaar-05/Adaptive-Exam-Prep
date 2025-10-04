// Update study time slider value display
const studyTimeSlider = document.getElementById('studyTime');
const studyTimeValue = document.getElementById('studyTimeValue');

studyTimeSlider.addEventListener('input', function() {
    studyTimeValue.textContent = this.value;
});

// Form validation
const signupForm = document.getElementById('signupForm');

signupForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form values
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const selectedClass = document.querySelector('input[name="class"]:checked');
    const selectedBoard = document.querySelector('input[name="exam_board"]:checked');
    const termsChecked = document.querySelector('input[name="terms"]:checked');
    
    // Validation
    if (!firstName || !lastName) {
        showAlert('Please enter your full name', 'error');
        return;
    }
    
    if (!email || !validateEmail(email)) {
        showAlert('Please enter a valid email address', 'error');
        return;
    }
    
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters long', 'error');
        return;
    }
    
    if (!selectedClass) {
        showAlert('Please select your current grade', 'error');
        return;
    }
    
    if (!selectedBoard) {
        showAlert('Please select your exam board', 'error');
        return;
    }
    
    if (!termsChecked) {
        showAlert('Please agree to the Terms of Service and Privacy Policy', 'error');
        return;
    }
    
    // If validation passes, submit the form
    this.submit();
});

// Email validation function
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show alert function
function showAlert(message, type) {
    const flashContainer = document.querySelector('.flash-messages') || createFlashContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    flashContainer.appendChild(alertDiv);
    
    // Remove alert after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// Social login buttons (placeholder functionality)
const googleBtn = document.querySelector('.google-btn');
const facebookBtn = document.querySelector('.facebook-btn');

googleBtn.addEventListener('click', function() {
    showAlert('Google sign-up is coming soon!', 'warning');
});

facebookBtn.addEventListener('click', function() {
    showAlert('Facebook sign-up is coming soon!', 'warning');
});

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});