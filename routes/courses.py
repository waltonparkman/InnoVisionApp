import logging
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Course, UserCourse, User, Quiz, UserQuizResult, StudyGroup
from services.ai_service import personalize_content, hybrid_recommendations, dynamic_difficulty_adjustment
from database import db
import numpy as np
from bleach import clean

bp = Blueprint('courses', __name__)

@bp.route('/courses')
@login_required
def course_list():
    courses = Course.query.all()
    all_users = User.query.all()
    try:
        recommended_courses = hybrid_recommendations(current_user, courses, all_users)
    except Exception as e:
        logging.error(f"Error in hybrid_recommendations: {str(e)}")
        recommended_courses = []
    return render_template('course_list.html', courses=courses, recommended_courses=recommended_courses)

@bp.route('/courses/<int:course_id>')
@login_required
def course_detail(course_id):
    logging.info(f"Accessing course detail for course_id: {course_id}, user_id: {current_user.id}")
    course = Course.query.get_or_404(course_id)
    user_course = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if not user_course:
        user_course = UserCourse(user_id=current_user.id, course_id=course_id, progress=0)
        db.session.add(user_course)
        db.session.commit()
    
    course_content = {
        'course_id': course.id,
        'title': course.title,
        'content': course.content,
    }
    logging.info(f"Course content prepared: {course_content}")
    
    personalized_content = personalize_content(current_user, course_content)
    logging.info(f"Personalized content received for user {current_user.id} and course {course_id}")
    
    all_users = User.query.all()
    all_courses = Course.query.all()
    recommended_courses = hybrid_recommendations(current_user, all_courses, all_users)
    
    adjusted_difficulty = dynamic_difficulty_adjustment(current_user, course_id)
    logging.info(f"Dynamically adjusted difficulty for user {current_user.id} and course {course_id}: {adjusted_difficulty}")
    
    return render_template('course_detail.html', 
                           course=course, 
                           personalized_content=personalized_content, 
                           user_progress=user_course.progress,
                           recommended_courses=recommended_courses,
                           adjusted_difficulty=adjusted_difficulty)

@bp.route('/courses/<int:course_id>/progress', methods=['POST'])
@login_required
def update_progress(course_id):
    user_course = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if user_course:
        user_course.progress += 10
        if user_course.progress > 100:
            user_course.progress = 100
        db.session.commit()
        return jsonify({'success': True, 'progress': user_course.progress})
    return jsonify({'success': False, 'error': 'Course not found'}), 404

@bp.route('/courses/<int:course_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(course_id):
    feedback = request.json.get('feedback')
    difficulty = request.json.get('difficulty')
    engagement = request.json.get('engagement')
    
    logging.info(f"Received feedback for course {course_id}: {feedback}")
    logging.info(f"Difficulty rating: {difficulty}")
    logging.info(f"Engagement rating: {engagement}")
    
    return jsonify({'success': True, 'message': 'Feedback received and processed'})

@bp.route('/courses/recommendations')
@login_required
def get_recommendations():
    all_courses = Course.query.all()
    all_users = User.query.all()
    try:
        recommended_courses = hybrid_recommendations(current_user, all_courses, all_users)
    except Exception as e:
        logging.error(f"Error in hybrid_recommendations: {str(e)}")
        recommended_courses = []
    return jsonify([{'id': course.id, 'title': course.title, 'description': course.description} for course in recommended_courses])

@bp.route('/courses/<int:course_id>/quiz', methods=['GET', 'POST'])
@login_required
def course_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    quiz = Quiz.query.filter_by(course_id=course_id).first()
    
    if request.method == 'POST':
        score = calculate_quiz_score(quiz, request.form)
        user_quiz_result = UserQuizResult(user_id=current_user.id, quiz_id=quiz.id, score=score)
        db.session.add(user_quiz_result)
        db.session.commit()
        
        return jsonify({'success': True, 'score': score})
    
    return render_template('quiz.html', course=course, quiz=quiz)

def calculate_quiz_score(quiz, form_data):
    correct_answers = 0
    total_questions = len(quiz.questions)
    
    for question, answer in quiz.questions.items():
        if form_data.get(question) == answer:
            correct_answers += 1
    
    return (correct_answers / total_questions) * 100

@bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content = request.form.get('content')
        
        logging.info(f"Received course creation request - Title: {title}")
        logging.info(f"Description: {description[:100]}...")  # Log first 100 characters
        logging.info(f"Content: {content[:100]}...")  # Log first 100 characters
        
        try:
            # Sanitize the content
            content = clean(content, tags=['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img', 'blockquote', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'], attributes={'a': ['href', 'title'], 'img': ['src', 'alt']})
            
            new_course = Course(title=title, description=description, content=content)
            db.session.add(new_course)
            db.session.commit()
            
            logging.info(f"Course created successfully - ID: {new_course.id}, Title: {title}")
            flash('Course created successfully!', 'success')
            return redirect(url_for('courses.course_list'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating course: {str(e)}")
            flash('An error occurred while creating the course. Please try again.', 'error')
    
    return render_template('create_course.html')

@bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.content = clean(request.form.get('content'), tags=['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img', 'blockquote', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'], attributes={'a': ['href', 'title'], 'img': ['src', 'alt']})
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses.course_detail', course_id=course.id))
    
    return render_template('edit_course.html', course=course)

@bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    study_groups = StudyGroup.query.filter_by(course_id=course_id).all()
    for study_group in study_groups:
        db.session.delete(study_group)
    
    user_courses = UserCourse.query.filter_by(course_id=course_id).all()
    for user_course in user_courses:
        db.session.delete(user_course)
    
    db.session.delete(course)
    
    try:
        db.session.commit()
        flash('Course and associated study groups deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting course: {str(e)}")
        flash('An error occurred while deleting the course. Please try again.', 'error')
    
    return redirect(url_for('courses.course_list'))
