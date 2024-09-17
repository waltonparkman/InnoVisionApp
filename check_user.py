from main import app, db
from models import User
import sys

def check_user(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password hash: {user.password_hash}")
        else:
            print(f"User not found: {username}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_user(sys.argv[1])
    else:
        print("Please provide a username as a command-line argument.")
