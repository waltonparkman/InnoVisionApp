import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, vstack
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
import logging
from datetime import datetime, timedelta
from sklearn.mixture import GaussianMixture

learning_styles = ['visual', 'auditory', 'kinesthetic', 'reading/writing']
sample_responses = [
    "I prefer diagrams and charts",
    "I learn best through lectures and discussions",
    "Hands-on activities help me understand better",
    "I enjoy reading textbooks and writing notes",
    "Watching educational videos is my preferred method",
    "I like to listen to podcasts and audiobooks",
    "Building models and doing experiments works best for me",
    "Taking detailed notes helps me remember information"
]
sample_labels = [0, 1, 2, 3, 0, 1, 2, 3]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sample_responses)
X_train, X_test, y_train, y_test = train_test_split(X, sample_labels, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

user_features = np.array([
    [0.8, 0.7, 0.9, 0.6, 0.5],
    [0.6, 0.5, 0.7, 0.4, 0.3],
    [0.9, 0.8, 0.95, 0.8, 0.7],
    [0.3, 0.4, 0.5, 0.2, 0.1]
])
difficulty_levels = np.array([0.7, 0.5, 0.8, 0.3])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(user_features)

gbr = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gbr.fit(X_scaled, difficulty_levels)

def assess_learning_style(questionnaire_data):
    responses = [q['answer'] for q in questionnaire_data]
    X_new = vectorizer.transform(responses)
    predictions = clf.predict(X_new)
    learning_style_index = np.bincount(predictions).argmax()
    return learning_styles[learning_style_index]

def calculate_user_performance(user, course_id):
    user_course = next((uc for uc in user.user_courses if uc.course_id == course_id), None)
    return user_course.progress if user_course else 0.5

def calculate_time_spent(user, course_id):
    user_course = next((uc for uc in user.user_courses if uc.course_id == course_id), None)
    if user_course:
        time_diff = datetime.utcnow() - user.last_login
        return min(time_diff.total_seconds() / 3600, 10) / 10
    return 0.5

def calculate_engagement_level(user, course_id):
    return user.engagement_score()

def calculate_prior_knowledge(user, course_id):
    related_courses = [uc for uc in user.user_courses if uc.course_id != course_id]
    if related_courses:
        return sum(uc.progress for uc in related_courses) / len(related_courses) / 100
    return 0.5

def calculate_quiz_performance(user, course_id):
    from models import UserQuizResult, Quiz
    quiz_results = UserQuizResult.query.join(Quiz).filter(
        UserQuizResult.user_id == user.id,
        Quiz.course_id == course_id
    ).all()
    
    if not quiz_results:
        return 0.5
    
    average_score = sum(result.score for result in quiz_results) / len(quiz_results)
    return average_score / 100

def adapt_content_difficulty(user_performance, time_spent, engagement_level, prior_knowledge, learning_pace, quiz_performance):
    user_features = np.array([[user_performance, time_spent, engagement_level, prior_knowledge, learning_pace, quiz_performance]])
    user_features_scaled = scaler.transform(user_features)
    predicted_difficulty = gbr.predict(user_features_scaled)[0]
    
    if predicted_difficulty > 0.7:
        return 'hard'
    elif predicted_difficulty > 0.4:
        return 'medium'
    else:
        return 'easy'

def adapt_to_learning_style(content, learning_style):
    adaptations = {
        'visual': "Enhanced with more diagrams, charts, and visual aids",
        'auditory': "Supplemented with audio explanations and discussions",
        'kinesthetic': "Enriched with interactive simulations and hands-on exercises",
        'reading/writing': "Expanded with detailed written explanations and note-taking guides"
    }
    return adaptations.get(learning_style, "No specific adaptation")

def generate_adapted_content(content, learning_style, difficulty):
    if content is None:
        content = "No content available for this course."
    adapted_content = f"Adapted content for {learning_style} learners at {difficulty} difficulty:\n\n"
    
    if learning_style == 'visual':
        adapted_content += "Visual Learning Adaptations for Python:\n"
        adapted_content += "1. Create a flowchart illustrating the Python program execution flow.\n"
        adapted_content += "2. Develop a mind map connecting Python data types and their relationships.\n"
        adapted_content += "3. Design an infographic showcasing Python's most common built-in functions.\n"
        adapted_content += "4. Watch a video demonstration of Python code execution using a visualizer tool.\n"
    elif learning_style == 'auditory':
        adapted_content += "Auditory Learning Adaptations:\n"
        adapted_content += "1. Listen to a podcast discussing Python's core concepts and best practices.\n"
        adapted_content += "2. Participate in a group discussion about Python's role in data science and web development.\n"
        adapted_content += "3. Record yourself explaining key Python concepts and listen to it for reinforcement.\n"
    elif learning_style == 'kinesthetic':
        adapted_content += "Kinesthetic Learning Adaptations for Python:\n"
        adapted_content += "1. Complete hands-on coding exercises in an interactive Python environment.\n"
        adapted_content += "2. Build a small Python project that demonstrates the concepts you've learned.\n"
        adapted_content += "3. Use physical objects to represent Python data structures and manipulate them.\n"
    else:  # reading/writing
        adapted_content += "Reading/Writing Learning Adaptations for Python:\n"
        adapted_content += "1. Write a detailed summary of Python's core data types and their methods.\n"
        adapted_content += "2. Create flashcards with Python syntax rules and common coding patterns.\n"
        adapted_content += "3. Develop a set of practice questions covering Python fundamentals.\n"
    
    if difficulty == 'easy':
        adapted_content += "\nEasy Difficulty Adaptations for Python:\n"
        adapted_content += "- We'll start with basic Python syntax and simple data types.\n"
        adapted_content += "- Examples will focus on straightforward operations and built-in functions.\n"
        adapted_content += "- Practice exercises will reinforce fundamental Python concepts.\n"
        adapted_content += "\nExample Python code (Easy):\n"
        adapted_content += """
# Basic variable assignment and string manipulation
name = "Alice"
age = 30
print(f"Hello, my name is {name} and I am {age} years old.")
"""
    elif difficulty == 'medium':
        adapted_content += "\nMedium Difficulty Adaptations for Python:\n"
        adapted_content += "- We'll explore more complex data structures like lists, dictionaries, and tuples.\n"
        adapted_content += "- Examples will include working with functions and basic object-oriented programming.\n"
        adapted_content += "- Practice exercises will require applying Python concepts to solve real-world problems.\n"
        adapted_content += "\nExample Python code (Medium):\n"
        adapted_content += """
# Function to calculate the factorial of a number using recursion
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Using a list comprehension to generate a list of factorials
factorials = [factorial(i) for i in range(1, 6)]
print(f"Factorials of numbers 1 to 5: {factorials}")
"""
    else:  # hard
        adapted_content += "\nAdvanced Difficulty Adaptations for Python:\n"
        adapted_content += "- We'll delve into advanced topics like decorators, generators, and context managers.\n"
        adapted_content += "- Examples will showcase complex, real-world scenarios using Python libraries and frameworks.\n"
        adapted_content += "- Practice exercises will challenge you to optimize code and implement design patterns.\n"
        adapted_content += "\nExample Python code (Hard):\n"
        adapted_content += """
# Implementing a decorator to measure function execution time
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def complex_operation(n):
    return sum(i * i for i in range(n))

result = complex_operation(1000000)
print(f"Result: {result}")
"""
    
    adapted_content += f"\nOriginal Content:\n{content}\n"
    
    return adapted_content

def recommend_resources(user, course_id):
    learning_style = user.learning_style or 'visual'
    user_course = next((uc for uc in user.user_courses if uc.course_id == course_id), None)
    progress = user_course.progress if user_course else 0
    difficulty = adapt_content_difficulty(progress, calculate_time_spent(user, course_id), 
                                          user.engagement_score(), calculate_prior_knowledge(user, course_id), 
                                          user.learning_pace(), calculate_quiz_performance(user, course_id))
    
    resources = []
    
    if learning_style == 'visual':
        resources.append("Interactive Python visualization library tutorial (e.g., Matplotlib, Seaborn)")
        resources.append("Video series on Python data structures and algorithms with visualizations")
        resources.append("Python coding challenges for visual learners with graphical outputs")
    elif learning_style == 'auditory':
        resources.append("Podcast series discussing Python best practices and design patterns")
        resources.append("Audio lectures on advanced Python concepts by industry experts")
    elif learning_style == 'kinesthetic':
        resources.append("Interactive Python coding environment with hands-on exercises")
        resources.append("Python project-based learning tutorials")
    else:  # reading/writing
        resources.append("Comprehensive e-book on Python programming techniques")
        resources.append("Academic paper analyzing recent developments in Python frameworks")
    
    if difficulty == 'easy':
        resources.append("Beginner's guide to Python syntax and basic concepts")
    elif difficulty == 'medium':
        resources.append("Intermediate Python programming cookbook with practical examples")
        resources.append("Video series on intermediate Python concepts and their applications")
    else:  # hard
        resources.append("Advanced Python design patterns and optimization techniques")
        resources.append("Research paper on cutting-edge Python applications in data science and AI")
    
    if progress < 50:
        resources.append("Quick reference guide for Python built-in functions and modules")
    else:
        resources.append("Advanced problem set for Python algorithm implementation and optimization")
    
    return resources

def generate_adaptive_learning_path(user, course_id):
    learning_style = user.learning_style or 'visual'
    user_course = next((uc for uc in user.user_courses if uc.course_id == course_id), None)
    progress = user_course.progress if user_course else 0
    performance = user.average_performance()
    engagement = user.engagement_score()
    
    path = ["Introduction to Python programming fundamentals"]
    
    if learning_style == 'visual':
        path.append("Visual exploration of Python data types and structures")
        path.append("Flowchart creation for Python control structures")
    elif learning_style == 'auditory':
        path.append("Audio introduction to Python syntax and basic concepts")
        path.append("Group discussion on Python's role in modern software development")
    elif learning_style == 'kinesthetic':
        path.append("Hands-on coding exercises with Python's basic data types")
        path.append("Interactive Python function and module exercises")
    else:  # reading/writing
        path.append("Comprehensive reading on Python syntax and data types")
        path.append("Written exercises on Python control structures and functions")
    
    if performance > 0.7:
        path.append("Advanced Python concepts: decorators, generators, and context managers")
        path.append("Complex problem-solving using Python libraries and frameworks")
    elif performance > 0.4:
        path.append("Intermediate Python: object-oriented programming and file handling")
        path.append("Guided practice with Python modules and packages")
    else:
        path.append("Review of Python basics: variables, loops, and conditional statements")
        path.append("Additional examples and explanations of Python functions")
    
    if engagement > 0.6:
        path.append("Challenging Python projects: building a web scraper or data analysis tool")
    else:
        path.append("Interactive quizzes on Python concepts to boost engagement")
    
    if progress > 75:
        path.append("Preparation for advanced Python certification")
    elif progress > 50:
        path.append("Mid-course project: building a Python application")
    else:
        path.append("Basic Python programming milestone check-in")
    
    path.append("Final assessment of Python skills and future learning recommendations")
    
    return path

def content_based_recommendations(user, all_courses):
    user_courses = user.user_courses
    user_course_vectors = [vectorizer.transform([f"{uc.course.description or ''} {uc.course.content or ''}"]) for uc in user_courses if uc.course]
    if not user_course_vectors:
        return np.zeros(len(all_courses))
    
    user_profile = vstack(user_course_vectors).mean(axis=0)
    
    all_course_vectors = vectorizer.transform([f"{course.description or ''} {course.content or ''}" for course in all_courses])
    
    n_components = min(100, all_course_vectors.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    lsa = Pipeline([('svd', svd)])
    
    all_course_vectors_lsa = lsa.fit_transform(all_course_vectors)
    user_profile_lsa = lsa.transform(user_profile)
    
    similarities = cosine_similarity(user_profile_lsa, all_course_vectors_lsa)
    
    return similarities.flatten()

def collaborative_filtering_recommendations(user, all_courses, all_users):
    user_course_matrix = np.zeros((len(all_users), len(all_courses)))
    for i, u in enumerate(all_users):
        for j, c in enumerate(all_courses):
            user_course = next((uc for uc in u.user_courses if uc.course_id == c.id), None)
            user_course_matrix[i, j] = user_course.progress if user_course else 0

    course_similarity = cosine_similarity(user_course_matrix.T)
    user_ratings = user_course_matrix[all_users.index(user)]
    
    recommendations = []
    for i, course in enumerate(all_courses):
        if user_ratings[i] == 0:  # User hasn't taken this course
            similar_courses = course_similarity[i]
            course_score = np.sum(similar_courses * user_ratings) / np.sum(np.abs(similar_courses))
            recommendations.append((course, course_score))
    
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [course for course, _ in recommendations[:5]]

def hybrid_recommendations(user, all_courses, users, n_recommendations=5):
    content_based_scores = content_based_recommendations(user, all_courses)
    collaborative_recommendations = collaborative_filtering_recommendations(user, all_courses, users)

    hybrid_scores = []
    for i, course in enumerate(all_courses):
        content_score = content_based_scores[i]
        collab_score = 1 if course in collaborative_recommendations else 0
        hybrid_score = 0.7 * content_score + 0.3 * collab_score
        hybrid_scores.append((course, hybrid_score))

    hybrid_scores.sort(key=lambda x: x[1], reverse=True)
    return [course for course, _ in hybrid_scores[:n_recommendations]]

def dynamic_difficulty_adjustment(user, course_id):
    user_course = next((uc for uc in user.user_courses if uc.course_id == course_id), None)
    if not user_course:
        return 'medium'  # Default difficulty

    progress = user_course.progress
    quiz_performance = calculate_quiz_performance(user, course_id)
    engagement_level = calculate_engagement_level(user, course_id)
    time_spent = calculate_time_spent(user, course_id)
    learning_pace = user.learning_pace()

    X = np.array([[progress, quiz_performance, engagement_level, time_spent, learning_pace]])
    X_scaled = scaler.transform(X)

    predicted_difficulty = gbr.predict(X_scaled)[0]

    if predicted_difficulty > 0.7:
        return 'hard'
    elif predicted_difficulty > 0.4:
        return 'medium'
    else:
        return 'easy'

def personalize_content(user, course_content):
    logging.info(f"Starting content personalization for user {user.id} and course {course_content['course_id']}")
    try:
        learning_style = user.learning_style or 'visual'
        logging.info(f"User learning style: {learning_style}")
        
        try:
            user_performance = calculate_user_performance(user, course_content['course_id'])
            logging.info(f"User performance: {user_performance}")
        except Exception as e:
            logging.error(f"Error calculating user performance: {str(e)}")
            user_performance = 0.5  # default value
        
        try:
            time_spent = calculate_time_spent(user, course_content['course_id'])
            logging.info(f"Time spent: {time_spent}")
        except Exception as e:
            logging.error(f"Error calculating time spent: {str(e)}")
            time_spent = 0.5  # default value
        
        try:
            engagement_level = calculate_engagement_level(user, course_content['course_id'])
            logging.info(f"Engagement level: {engagement_level}")
        except Exception as e:
            logging.error(f"Error calculating engagement level: {str(e)}")
            engagement_level = 0.5  # default value
        
        try:
            prior_knowledge = calculate_prior_knowledge(user, course_content['course_id'])
            logging.info(f"Prior knowledge: {prior_knowledge}")
        except Exception as e:
            logging.error(f"Error calculating prior knowledge: {str(e)}")
            prior_knowledge = 0.5  # default value
        
        try:
            learning_pace = user.learning_pace()
            logging.info(f"Learning pace: {learning_pace}")
        except Exception as e:
            logging.error(f"Error calculating learning pace: {str(e)}")
            learning_pace = 0.5  # default value
        
        try:
            quiz_performance = calculate_quiz_performance(user, course_content['course_id'])
            logging.info(f"Quiz performance: {quiz_performance}")
        except Exception as e:
            logging.error(f"Error calculating quiz performance: {str(e)}")
            quiz_performance = 0.5  # default value
        
        try:
            difficulty = dynamic_difficulty_adjustment(user, course_content['course_id'])
            logging.info(f"Dynamically adjusted difficulty: {difficulty}")
        except Exception as e:
            logging.error(f"Error in dynamic difficulty adjustment: {str(e)}")
            difficulty = 'medium'  # default value
        
        try:
            adapted_content = generate_adapted_content(course_content.get('content'), learning_style, difficulty)
            logging.info(f"Generated adapted content (first 100 characters): {adapted_content[:100]}...")
        except Exception as e:
            logging.error(f"Error generating adapted content: {str(e)}")
            adapted_content = "Error occurred while adapting content"
        
        try:
            learning_style_adaptations = adapt_to_learning_style(course_content.get('content', ''), learning_style)
            logging.info(f"Generated learning style adaptations: {learning_style_adaptations}")
        except Exception as e:
            logging.error(f"Error generating learning style adaptations: {str(e)}")
            learning_style_adaptations = "Unable to adapt content to learning style"
        
        try:
            recommended_resources = recommend_resources(user, course_content['course_id'])
            logging.info(f"Generated recommended resources: {recommended_resources}")
        except Exception as e:
            logging.error(f"Error generating recommended resources: {str(e)}")
            recommended_resources = []
        
        try:
            adaptive_path = generate_adaptive_learning_path(user, course_content['course_id'])
            logging.info(f"Generated adaptive learning path: {adaptive_path}")
        except Exception as e:
            logging.error(f"Error generating adaptive learning path: {str(e)}")
            adaptive_path = []
        
        try:
            from models import User, Course
            all_users = User.query.all()
            all_courses = Course.query.all()
            collab_recommendations = collaborative_filtering_recommendations(user, all_courses, all_users)
            logging.info(f"Generated collaborative filtering recommendations: {collab_recommendations}")
        except Exception as e:
            logging.error(f"Error generating collaborative filtering recommendations: {str(e)}")
            collab_recommendations = []
        
        personalized_content = {
            'original_content': course_content.get('content') or 'No content available',
            'adapted_content': adapted_content,
            'difficulty': difficulty,
            'learning_style_adaptations': learning_style_adaptations,
            'recommended_resources': recommended_resources,
            'adaptive_path': adaptive_path,
            'collaborative_recommendations': [course.title for course in collab_recommendations]
        }
        
        logging.info(f"Personalized content created successfully for user {user.id} and course {course_content['course_id']}")
        return personalized_content
    except Exception as e:
        logging.error(f"Unexpected error in personalize_content: {str(e)}")
        return {
            'original_content': course_content.get('content') or 'No content available',
            'adapted_content': 'Error occurred while personalizing content',
            'difficulty': 'unknown',
            'learning_style_adaptations': 'Unable to adapt content',
            'recommended_resources': [],
            'adaptive_path': [],
            'collaborative_recommendations': []
        }