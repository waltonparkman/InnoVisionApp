import logging
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Course, UserCourse, User, Quiz, UserQuizResult, StudyGroup
from services.ai_service import personalize_content, hybrid_recommendations, dynamic_difficulty_adjustment
from database import db
import numpy as np
import markdown2

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
        'content': markdown2.markdown(course.content, extras=['fenced-code-blocks', 'tables']),
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

@bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content = request.form.get('content')
        
        new_course = Course(title=title, description=description, content=content)
        db.session.add(new_course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('courses.course_detail', course_id=new_course.id))
    
    return render_template('create_course.html')

@bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.content = request.form.get('content')
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses.course_detail', course_id=course.id))
    
    return render_template('edit_course.html', course=course)

@bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Delete associated study groups
    StudyGroup.query.filter_by(course_id=course_id).delete()
    
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses.course_list'))

@bp.route('/courses/<int:course_id>/update_progress', methods=['POST'])
@login_required
def update_progress(course_id):
    user_course = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if user_course:
        user_course.progress = min(user_course.progress + 10, 100)
        db.session.commit()
        return jsonify({'success': True, 'progress': user_course.progress})
    
    return jsonify({'success': False}), 404

@bp.route('/courses/<int:course_id>/submit_feedback', methods=['POST'])
@login_required
def submit_feedback(course_id):
    data = request.json
    difficulty = data.get('difficulty')
    engagement = data.get('engagement')
    feedback = data.get('feedback')
    
    # Here you would typically store this feedback in the database
    # For now, we'll just log it
    logging.info(f"Feedback received for course {course_id}: Difficulty: {difficulty}, Engagement: {engagement}, Feedback: {feedback}")
    
    return jsonify({'success': True})
