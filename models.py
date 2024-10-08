from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    learning_style = db.Column(db.String(64))
    user_courses = db.relationship('UserCourse', back_populates='user')
    quiz_results = db.relationship('UserQuizResult', back_populates='user')
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    total_study_time = db.Column(db.Integer, default=0)  # in minutes
    study_groups = db.relationship('StudyGroup', secondary='user_study_group', back_populates='members')
    forum_posts = db.relationship('ForumPost', back_populates='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def average_performance(self):
        if not self.user_courses:
            return 0
        return sum(uc.progress for uc in self.user_courses) / len(self.user_courses)

    def engagement_score(self):
        if not self.user_courses or self.last_login is None:
            return 0
        
        days_since_login = (datetime.utcnow() - self.last_login).days + 1
        login_frequency = len(self.user_courses) / days_since_login
        
        max_study_time = days_since_login * 4 * 60
        normalized_study_time = min(self.total_study_time / max_study_time, 1)
        
        engagement = (0.5 * login_frequency) + (0.5 * normalized_study_time)
        return min(engagement, 1)

    def learning_pace(self):
        if not self.user_courses or not self.total_study_time:
            return 0.5
        
        total_progress = sum(uc.progress for uc in self.user_courses)
        progress_per_hour = total_progress / (self.total_study_time / 60)
        
        normalized_pace = progress_per_hour / 10
        
        performance_factor = self.average_performance()
        adjusted_pace = (normalized_pace + performance_factor) / 2
        
        return min(max(adjusted_pace, 0), 1)

    def update_study_time(self, minutes):
        self.total_study_time += minutes
        db.session.commit()

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    user_courses = db.relationship('UserCourse', back_populates='course')
    quizzes = db.relationship('Quiz', back_populates='course')
    study_groups = db.relationship('StudyGroup', back_populates='course')
    forum_posts = db.relationship('ForumPost', back_populates='course')

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    user = db.relationship('User', back_populates='user_courses')
    course = db.relationship('Course', back_populates='user_courses')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    questions = db.Column(db.JSON)
    course = db.relationship('Course', back_populates='quizzes')
    user_results = db.relationship('UserQuizResult', back_populates='quiz')

class UserQuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', back_populates='quiz_results')
    quiz = db.relationship('Quiz', back_populates='user_results')

class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course = db.relationship('Course', back_populates='study_groups')
    members = db.relationship('User', secondary='user_study_group', back_populates='study_groups')

class UserStudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    study_group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author = db.relationship('User', back_populates='forum_posts')
    course = db.relationship('Course', back_populates='forum_posts')
    replies = db.relationship('ForumReply', back_populates='post', cascade='all, delete-orphan')

class ForumReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    author = db.relationship('User')
    post = db.relationship('ForumPost', back_populates='replies')