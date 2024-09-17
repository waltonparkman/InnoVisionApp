from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, StudyGroup, UserStudyGroup, ForumPost, ForumReply, Course
from datetime import datetime

bp = Blueprint('peer_learning', __name__)

@bp.route('/study_groups')
@login_required
def study_groups():
    study_groups = StudyGroup.query.all()
    return render_template('study_groups.html', study_groups=study_groups)

@bp.route('/study_groups/create', methods=['GET', 'POST'])
@login_required
def create_study_group():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        course_id = request.form.get('course_id')
        
        new_group = StudyGroup(name=name, description=description, course_id=course_id)
        db.session.add(new_group)
        db.session.commit()
        
        user_group = UserStudyGroup(user_id=current_user.id, study_group_id=new_group.id)
        db.session.add(user_group)
        db.session.commit()
        
        flash('Study group created successfully!', 'success')
        return redirect(url_for('peer_learning.study_groups'))
    
    courses = Course.query.all()
    return render_template('create_study_group.html', courses=courses)

@bp.route('/study_groups/<int:group_id>/join')
@login_required
def join_study_group(group_id):
    study_group = StudyGroup.query.get_or_404(group_id)
    if current_user not in study_group.members:
        user_group = UserStudyGroup(user_id=current_user.id, study_group_id=group_id)
        db.session.add(user_group)
        db.session.commit()
        flash('You have joined the study group!', 'success')
    else:
        flash('You are already a member of this study group.', 'info')
    return redirect(url_for('peer_learning.study_groups'))

@bp.route('/study_groups/<int:group_id>')
@login_required
def study_group_detail(group_id):
    study_group = StudyGroup.query.get_or_404(group_id)
    return render_template('study_group_detail.html', study_group=study_group)

@bp.route('/forum')
@login_required
def forum():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    return render_template('forum.html', posts=posts)

@bp.route('/forum/create', methods=['GET', 'POST'])
@login_required
def create_forum_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        course_id = request.form.get('course_id')
        
        new_post = ForumPost(title=title, content=content, user_id=current_user.id, course_id=course_id)
        db.session.add(new_post)
        db.session.commit()
        
        flash('Forum post created successfully!', 'success')
        return redirect(url_for('peer_learning.forum'))
    
    courses = Course.query.all()
    return render_template('create_forum_post.html', courses=courses)

@bp.route('/forum/<int:post_id>')
@login_required
def forum_post_detail(post_id):
    post = ForumPost.query.get_or_404(post_id)
    return render_template('forum_post_detail.html', post=post)

@bp.route('/forum/<int:post_id>/reply', methods=['POST'])
@login_required
def forum_post_reply(post_id):
    post = ForumPost.query.get_or_404(post_id)
    content = request.form.get('content')
    
    new_reply = ForumReply(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(new_reply)
    db.session.commit()
    
    flash('Reply added successfully!', 'success')
    return redirect(url_for('peer_learning.forum_post_detail', post_id=post_id))
