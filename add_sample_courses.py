from main import app, db
from models import Course, User, UserCourse, Quiz, UserQuizResult
import random

def add_sample_data():
    with app.app_context():
        # Create sample courses
        courses = [
            Course(title="Introduction to Python", description="Learn the basics of Python programming language."),
            Course(title="Web Development with Flask", description="Build web applications using the Flask framework."),
            Course(title="Data Science Fundamentals", description="Explore the basics of data science and machine learning."),
        ]

        for course in courses:
            existing_course = Course.query.filter_by(title=course.title).first()
            if not existing_course:
                db.session.add(course)

        db.session.commit()

        # Create sample users
        users = [
            User(username="alice", email="alice@example.com"),
            User(username="bob", email="bob@example.com"),
            User(username="charlie", email="charlie@example.com"),
        ]

        for user in users:
            existing_user = User.query.filter_by(username=user.username).first()
            if not existing_user:
                user.set_password("password123")
                db.session.add(user)

        db.session.commit()

        # Add user progress for courses
        for user in User.query.all():
            for course in Course.query.all():
                user_course = UserCourse(user_id=user.id, course_id=course.id, progress=random.uniform(0, 100))
                db.session.add(user_course)

        db.session.commit()

        # Create sample quizzes
        quizzes = [
            Quiz(course_id=1, title="Python Basics Quiz", questions={"q1": "What is a variable?", "q2": "How do you define a function in Python?"}),
            Quiz(course_id=2, title="Flask Fundamentals Quiz", questions={"q1": "What is a route in Flask?", "q2": "How do you render a template in Flask?"}),
            Quiz(course_id=3, title="Data Science Concepts Quiz", questions={"q1": "What is machine learning?", "q2": "Explain the difference between supervised and unsupervised learning."}),
        ]

        for quiz in quizzes:
            existing_quiz = Quiz.query.filter_by(title=quiz.title).first()
            if not existing_quiz:
                db.session.add(quiz)

        db.session.commit()

        # Add sample quiz results
        for user in User.query.all():
            for quiz in Quiz.query.all():
                quiz_result = UserQuizResult(user_id=user.id, quiz_id=quiz.id, score=random.uniform(0, 100))
                db.session.add(quiz_result)

        db.session.commit()

    print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data()
