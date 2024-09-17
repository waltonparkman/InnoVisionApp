// Courses related JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const courseList = document.getElementById('course-list');
    const courseDetail = document.getElementById('course-detail');
    const quizContainer = document.getElementById('quiz-container');

    if (courseList) {
        loadCourses();
    }

    if (courseDetail) {
        const courseId = courseDetail.dataset.courseId;
        loadCourseContent(courseId);
    }

    if (quizContainer) {
        const courseId = quizContainer.dataset.courseId;
        loadQuiz(courseId);
    }
});

async function loadCourses() {
    try {
        const response = await fetch('/courses');
        if (response.ok) {
            const courses = await response.json();
            displayCourses(courses);
            courses.forEach(saveCourseOffline);
        } else {
            console.log('Failed to fetch courses from server. Loading offline courses.');
            const offlineCourses = await loadOfflineCourses();
            displayCourses(offlineCourses);
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        showMessage('Failed to load courses', 'error');
    }
}

function displayCourses(courses) {
    const courseList = document.getElementById('course-list');
    courseList.innerHTML = '';

    courses.forEach(course => {
        const courseElement = document.createElement('div');
        courseElement.className = 'course-card';
        courseElement.innerHTML = `
            <h3>${course.title}</h3>
            <p>${course.description}</p>
            <a href="/courses/${course.id}" class="btn">View Course</a>
            <button class="btn btn-secondary save-offline" data-course-id="${course.id}">Save Offline</button>
        `;
        courseList.appendChild(courseElement);
    });

    // Add event listeners for "Save Offline" buttons
    const saveOfflineButtons = document.querySelectorAll('.save-offline');
    saveOfflineButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const courseId = event.target.getAttribute('data-course-id');
            const course = courses.find(c => c.id == courseId);
            if (course) {
                saveCourseOffline(course);
            }
        });
    });
}

async function loadCourseContent(courseId) {
    try {
        const response = await fetch(`/courses/${courseId}`);
        if (response.ok) {
            const content = await response.json();
            displayCourseContent(content);
            saveCourseOffline(content);
        } else {
            console.log('Failed to fetch course content from server. Loading offline content.');
            const offlineCourses = await loadOfflineCourses();
            const offlineCourse = offlineCourses.find(c => c.id == courseId);
            if (offlineCourse) {
                displayCourseContent(offlineCourse);
            } else {
                showMessage('Course content not available offline', 'error');
            }
        }
    } catch (error) {
        console.error('Error loading course content:', error);
        showMessage('Failed to load course content', 'error');
    }
}

function displayCourseContent(content) {
    const courseDetail = document.getElementById('course-detail');
    courseDetail.innerHTML = `
        <h2>${content.title}</h2>
        <div class="course-content">${content.content}</div>
        <div class="course-progress">Progress: ${content.progress}%</div>
        <a href="/courses/${content.id}/quiz" class="btn">Take Quiz</a>
    `;
}

async function loadQuiz(courseId) {
    try {
        const response = await fetch(`/courses/${courseId}/quiz`);
        if (response.ok) {
            const quiz = await response.json();
            displayQuiz(quiz);
        } else {
            showMessage('Quiz not available offline', 'error');
        }
    } catch (error) {
        console.error('Error loading quiz:', error);
        showMessage('Failed to load quiz', 'error');
    }
}

function displayQuiz(quiz) {
    const quizContainer = document.getElementById('quiz-container');
    quizContainer.innerHTML = `
        <h2>${quiz.title}</h2>
        <form id="quiz-form">
            ${quiz.questions.map((question, index) => `
                <div class="question">
                    <p>${question.text}</p>
                    ${question.options.map(option => `
                        <label>
                            <input type="radio" name="q${index}" value="${option}">
                            ${option}
                        </label>
                    `).join('')}
                </div>
            `).join('')}
            <button type="submit" class="btn">Submit Quiz</button>
        </form>
    `;

    document.getElementById('quiz-form').addEventListener('submit', event => {
        event.preventDefault();
        submitQuiz(quiz.id);
    });
}

async function submitQuiz(quizId) {
    const form = document.getElementById('quiz-form');
    const formData = new FormData(form);
    const answers = {};

    for (let [name, value] of formData.entries()) {
        answers[name] = value;
    }

    try {
        const response = await fetch(`/courses/${quizId}/quiz/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(answers),
        });

        if (response.ok) {
            const result = await response.json();
            showQuizResult(result);
        } else {
            showMessage('Failed to submit quiz', 'error');
        }
    } catch (error) {
        console.error('Error submitting quiz:', error);
        showMessage('Failed to submit quiz. It will be submitted when you\'re back online.', 'warning');
        // Store the quiz answers locally for later submission
        localStorage.setItem(`quiz_${quizId}_answers`, JSON.stringify(answers));
    }
}

function showQuizResult(result) {
    const quizContainer = document.getElementById('quiz-container');
    quizContainer.innerHTML = `
        <h2>Quiz Result</h2>
        <p>Your score: ${result.score}%</p>
        <p>Course progress: ${result.progress}%</p>
        <a href="/dashboard" class="btn">Back to Dashboard</a>
    `;
}

// Function to check for and submit stored quiz answers when online
function submitStoredQuizzes() {
    if (navigator.onLine) {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('quiz_') && key.endsWith('_answers')) {
                const quizId = key.split('_')[1];
                const answers = JSON.parse(localStorage.getItem(key));
                submitQuiz(quizId, answers);
                localStorage.removeItem(key);
            }
        }
    }
}

// Check for stored quizzes to submit when the page loads and when coming back online
window.addEventListener('load', submitStoredQuizzes);
window.addEventListener('online', submitStoredQuizzes);
