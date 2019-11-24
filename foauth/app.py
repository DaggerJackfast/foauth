import os
import sqlite3

# Third-party libraries
from flask import Flask, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)


# Internal imports
from db import init_db_command
from user import User
from server_side import server_flow

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    return 'Hello'


# bp = Blueprint('auth', __name__, url_prefix='/auth') # Example
@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


app.register_blueprint(server_flow)

if __name__ == "__main__":
    ssl_context = "adhoc"
    certs_dir = "../certs"
    key_path = os.path.join(certs_dir, 'localhost-key.pem')
    cert_path = os.path.join(certs_dir, 'localhost.pem')
    if os.path.exists(certs_dir) and os.path.exists(key_path) and os.path.exists(cert_path):
        ssl_context = (cert_path, key_path)
    app.run(ssl_context=ssl_context, debug=True)
