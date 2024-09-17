from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
import logging

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logging.info(f"Login attempt for user: {username}")
        user = User.query.filter_by(username=username).first()
        if user is None:
            logging.warning(f"User not found: {username}")
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        if not user.check_password(password):
            logging.warning(f"Invalid password for user: {username}")
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        logging.info(f"User logged in successfully: {username}")
        return redirect(url_for('user.dashboard'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        logging.info("Authenticated user attempted to access registration page")
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        logging.info(f"Registration attempt - Username: {username}, Email: {email}")
        
        # Validate username
        user = User.query.filter_by(username=username).first()
        if user is not None:
            logging.warning(f"Registration failed - Username already exists: {username}")
            flash('Please use a different username.')
            return redirect(url_for('auth.register'))
        
        # Validate email
        user = User.query.filter_by(email=email).first()
        if user is not None:
            logging.warning(f"Registration failed - Email already exists: {email}")
            flash('Please use a different email address.')
            return redirect(url_for('auth.register'))
        
        # Create new user
        logging.info(f"Creating new user - Username: {username}, Email: {email}")
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Add user to database
        try:
            db.session.add(user)
            db.session.commit()
            logging.info(f"New user registered successfully: {username}")
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logging.error(f"Error during user registration: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')
