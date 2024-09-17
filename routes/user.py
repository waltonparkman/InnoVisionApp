from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import UserCourse, UserQuizResult, Quiz, db
from services.ai_service import assess_learning_style
from sqlalchemy import func

bp = Blueprint('user', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    user_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    course_progress = {}
    for uc in user_courses:
        course_title = uc.course.title if uc.course and uc.course.title else 'Unknown Course'
        if course_title not in course_progress or uc.progress > course_progress[course_title]:
            course_progress[course_title] = uc.progress
    course_progress = [{'course': course, 'progress': progress} for course, progress in course_progress.items()]
    
    quiz_results = db.session.query(
        Quiz.title,
        func.avg(UserQuizResult.score).label('average_score')
    ).join(UserQuizResult).filter(UserQuizResult.user_id == current_user.id).group_by(Quiz.title).all()
    
    return render_template('dashboard.html', course_progress=course_progress, quiz_results=quiz_results)

@bp.route('/assess_learning_style', methods=['POST'])
@login_required
def assess_learning_style():
    questionnaire_data = request.json
    learning_style = assess_learning_style(questionnaire_data)
    current_user.learning_style = learning_style
    db.session.commit()
    return jsonify({'learning_style': learning_style})

@bp.route('/progress')
@login_required
def get_progress():
    user_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    progress_data = [{'course': uc.course.title if uc.course and uc.course.title else 'Unknown Course', 'progress': uc.progress} for uc in user_courses]
    return jsonify(progress_data)
