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
        const courses = await response.json();
        displayCourses(courses);
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
        `;
        courseList.appendChild(courseElement);
    });
}

async function loadCourseContent(courseId) {
    try {
        const response = await fetch(`/courses/${courseId}`);
        const content = await response.json();
        displayCourseContent(content);
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
        const quiz = await response.json();
        displayQuiz(quiz);
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

        const result = await response.json();
        showQuizResult(result);
    } catch (error) {
        console.error('Error submitting quiz:', error);
        showMessage('Failed to submit quiz', 'error');
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
