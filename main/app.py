import uuid
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import Flask, jsonify, request, make_response
from flask_login import LoginManager, logout_user, login_required
from main.models import db_setup, User, db, Group
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecretkey'
db_setup(app)
login_manager = LoginManager(app)
login_manager.init_app(app)


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email
        })
    return jsonify({'users': output})


@app.route('/login', methods=['POST'])
def login():
    auth = request.form

    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm = "Login required !!"'}
        )

    user = User.query.filter_by(email=auth.get('email')).first()

    if not user:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm = "User does not exist !!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
        return make_response(token)
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


@app.route('/signup', methods=['POST'])
def register_user():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return make_response('Successfully registered.', 201)
    else:
        return make_response('User already exists. Please login', 202)


@app.route('/logout')
@token_required
def logout(current_user):
    return 'User logged out successfully'


@app.route('/createGroup', methods=['POST'])
def createGroup():
    body = request.get_json()
    name = body.get('name')
    admin = body.get('admin')
    users = body.get('list_of_users')
    create_time = datetime.utcnow()

    group = Group(
        name=name,
        admin=admin,
        users=users,
        create_time=create_time
    )
    db.session.add(group)
    db.session.commit()
    return make_response('Success', 200)
