from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from database import db
import logging

app = Flask(__name__)
app.config.from_object('config')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import auth, courses, user

app.register_blueprint(auth.bp)
app.register_blueprint(courses.bp)
app.register_blueprint(user.bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
