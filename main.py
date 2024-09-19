from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from database import db
import logging
import markdown
from markupsafe import Markup

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

from routes import auth, courses, user, peer_learning

app.register_blueprint(auth.bp)
app.register_blueprint(courses.bp)
app.register_blueprint(user.bp)
app.register_blueprint(peer_learning.bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offline')
def offline():
    return render_template('offline.html')

@app.route('/static/js/service-worker.js')
def serve_service_worker():
    return send_from_directory(app.static_folder, 'js/service-worker.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/json')

@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown.markdown(text, extensions=['extra']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
