// Main JavaScript file for common functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any common elements or event listeners here
    initNavigation();
});

function initNavigation() {
    const nav = document.querySelector('nav');
    if (nav) {
        nav.addEventListener('click', function(event) {
            if (event.target.tagName === 'A') {
                event.preventDefault();
                navigateTo(event.target.getAttribute('href'));
            }
        });
    }
}

function navigateTo(url) {
    // You can implement custom navigation logic here if needed
    window.location.href = url;
}

function showMessage(message, type = 'info') {
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        console.error('Message container not found');
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.className = `message ${type}`;

    messageContainer.appendChild(messageElement);

    // Remove the message after 5 seconds
    setTimeout(() => {
        messageContainer.removeChild(messageElement);
    }, 5000);
}

// Add more common functions as needed
