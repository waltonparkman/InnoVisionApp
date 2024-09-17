from flask import Blueprint, render_template
from flask_login import login_required
from models import Course

bp = Blueprint('courses', __name__)

@bp.route('/courses')
@login_required
def course_list():
    courses = Course.query.all()
    return render_template('course_list.html', courses=courses)

@bp.route('/courses/<int:course_id>')
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)
