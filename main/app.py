from flask import Flask, jsonify, request, flash
from flask_login import LoginManager, logout_user, login_user, current_user, login_required
from main.config import Config
from main.models import db_setup, User, db

app = Flask(__name__)
app.config.from_object(Config)
db_setup(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
# login_manager.login_view = 'login'


@app.route('/')
@login_required
def health_check():
    return jsonify(
        {
            'message': 'I am healthy!'
        }
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/signup', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user = User(
        username=username,
        email=email
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'success': True,
        'User': username
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        flash('Invalid user name or password')
        return "Invalid credentials or unauthorized access"

    login_user(user)
    print(current_user.username)
    return 'user login successful'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'User logged out successfully'

