// Main JavaScript file for common functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any common elements or event listeners here
    initNavigation();
    initOfflineStorage();
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

function initOfflineStorage() {
    if ('indexedDB' in window) {
        let db;
        const request = indexedDB.open('LearnAIOfflineDB', 1);

        request.onerror = function(event) {
            console.error('IndexedDB error:', event.target.error);
        };

        request.onsuccess = function(event) {
            db = event.target.result;
            console.log('IndexedDB initialized successfully');
        };

        request.onupgradeneeded = function(event) {
            db = event.target.result;
            const objectStore = db.createObjectStore('courses', { keyPath: 'id' });
            objectStore.createIndex('title', 'title', { unique: false });
            console.log('IndexedDB object store created');
        };
    }
}

function saveCourseOffline(course) {
    if ('indexedDB' in window) {
        const request = indexedDB.open('LearnAIOfflineDB', 1);

        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction(['courses'], 'readwrite');
            const objectStore = transaction.objectStore('courses');
            const addRequest = objectStore.put(course);

            addRequest.onsuccess = function() {
                console.log('Course saved offline:', course.title);
                showMessage('Course saved for offline use', 'success');
            };

            addRequest.onerror = function() {
                console.error('Error saving course offline:', addRequest.error);
                showMessage('Failed to save course for offline use', 'error');
            };
        };
    }
}

function loadOfflineCourses() {
    return new Promise((resolve, reject) => {
        if ('indexedDB' in window) {
            const request = indexedDB.open('LearnAIOfflineDB', 1);

            request.onsuccess = function(event) {
                const db = event.target.result;
                const transaction = db.transaction(['courses'], 'readonly');
                const objectStore = transaction.objectStore('courses');
                const getAllRequest = objectStore.getAll();

                getAllRequest.onsuccess = function() {
                    resolve(getAllRequest.result);
                };

                getAllRequest.onerror = function() {
                    reject(getAllRequest.error);
                };
            };

            request.onerror = function(event) {
                reject(event.target.error);
            };
        } else {
            reject(new Error('IndexedDB not supported'));
        }
    });
}

// Add more common functions as needed
