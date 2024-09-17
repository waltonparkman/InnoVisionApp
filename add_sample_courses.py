from main import app, db
from models import Course, User, UserCourse, Quiz, UserQuizResult, StudyGroup
import random
from datetime import datetime, timedelta

def add_sample_data():
    with app.app_context():
        # Create sample courses
        courses = [
            Course(
                title="Introduction to Python",
                description="Learn the basics of Python programming language.",
                content="""
Python is a high-level, interpreted programming language known for its simplicity and readability.

Key Concepts:
1. Variables and Data Types
2. Control Structures (if statements, loops)
3. Functions and Modules
4. Object-Oriented Programming
5. File Handling and Exceptions

Example Code:
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))

# Lists and list comprehension
numbers = [1, 2, 3, 4, 5]
squares = [n**2 for n in numbers]
print(f"Original numbers: {numbers}")
print(f"Squared numbers: {squares}")

# Dictionary example
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}
print(f"Person details: {person}")

Practice Exercise:
Write a function that takes a list of numbers and returns the sum of all even numbers in the list.
                """
            ),
            Course(
                title="Intermediate Python",
                description="Dive deeper into Python with advanced concepts and techniques.",
                content="""
This course builds upon the basics of Python, introducing more complex concepts and practical applications.

Key Concepts:
1. Advanced Data Structures (sets, named tuples)
2. Functional Programming in Python
3. Decorators and Generators
4. Context Managers
5. Concurrency and Parallelism

Example Code:
# Decorator example
def timing_decorator(func):
    from time import time
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        print(f"{func.__name__} executed in {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(2)
    print("Function executed")

slow_function()

# Generator example
def fibonacci_generator(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

fib = list(fibonacci_generator(10))
print(f"First 10 Fibonacci numbers: {fib}")

Practice Exercise:
Implement a context manager for handling file operations that automatically closes the file and handles exceptions.
                """
            ),
            Course(
                title="Python for Data Science",
                description="Learn how to use Python for data analysis and machine learning.",
                content="""
Explore the powerful libraries and tools in Python's ecosystem for data science and machine learning.

Key Concepts:
1. NumPy for numerical computing
2. Pandas for data manipulation
3. Matplotlib and Seaborn for data visualization
4. Scikit-learn for machine learning
5. Jupyter Notebooks for interactive development

Example Code:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Generate sample data
np.random.seed(42)
X = np.random.rand(100, 1)
y = 2 + 3 * X + np.random.randn(100, 1) * 0.1

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Visualize the results
plt.scatter(X_test, y_test, color='b', label='Actual')
plt.plot(X_test, y_pred, color='r', label='Predicted')
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.title('Linear Regression Example')
plt.show()

Practice Exercise:
Use Pandas to load a dataset of your choice, perform some basic data cleaning and analysis, and create a visualization using Matplotlib or Seaborn.
                """
            ),
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
                user.learning_style = random.choice(['visual', 'auditory', 'kinesthetic', 'reading/writing'])
                user.last_login = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                user.total_study_time = random.randint(60, 3000)  # 1 to 50 hours
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
            Quiz(course_id=1, title="Python Basics Quiz", questions={
                "q1": "What is a variable in Python?",
                "q2": "How do you define a function in Python?",
                "q3": "What is the difference between a list and a tuple in Python?",
                "q4": "Explain the concept of object-oriented programming in Python.",
                "q5": "How do you handle exceptions in Python?"
            }),
            Quiz(course_id=2, title="Intermediate Python Quiz", questions={
                "q1": "What is a decorator in Python?",
                "q2": "Explain the concept of a generator in Python.",
                "q3": "What is a context manager and how is it used?",
                "q4": "Describe the difference between multiprocessing and multithreading in Python.",
                "q5": "What are lambda functions and when should they be used?"
            }),
            Quiz(course_id=3, title="Python for Data Science Quiz", questions={
                "q1": "What is NumPy and why is it used in data science?",
                "q2": "Explain the difference between a Series and a DataFrame in Pandas.",
                "q3": "What is the purpose of train_test_split in scikit-learn?",
                "q4": "Describe the k-means clustering algorithm and its implementation in scikit-learn.",
                "q5": "What are the main types of plots in Matplotlib and when should each be used?"
            }),
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

        # Add sample study groups
        add_sample_study_groups()

    print("Sample data added successfully!")

def add_sample_study_groups():
    with app.app_context():
        courses = Course.query.all()
        users = User.query.all()
        
        for course in courses:
            group_name = f"{course.title} Study Group"
            description = f"A study group for students taking {course.title}"
            new_group = StudyGroup(name=group_name, description=description, course_id=course.id)
            db.session.add(new_group)
            
            # Add some random users to the group
            for _ in range(3):
                user = random.choice(users)
                if user not in new_group.members:
                    new_group.members.append(user)
        
        db.session.commit()
    
    print("Sample study groups added successfully!")

if __name__ == "__main__":
    add_sample_data()
