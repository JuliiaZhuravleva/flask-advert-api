from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

from models import db, Advert, User
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)


class ApiError(Exception):
    def __init__(self, status_code, msg):
        self.status_code = status_code
        self.msg = msg


@app.errorhandler(ApiError)
def handle_api_error(error):
    response = jsonify({'error': error.msg})
    response.status_code = error.status_code
    return response


def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(password, password_hash):
    return bcrypt.check_password_hash(password_hash, password)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise ApiError(401, 'Authorization header is missing')

        try:
            email, password = auth_header.split(':')
        except ValueError:
            raise ApiError(401, 'Invalid authorization header')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password(password, user.password_hash):
            raise ApiError(401, 'Invalid credentials')

        return f(*args, user=user, **kwargs)

    return decorated_function


class UserView(MethodView):
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise ApiError(404, 'User not found')
        return jsonify(user.to_dict())

    def post(self):
        data = request.json
        if not data or 'email' not in data or 'password' not in data:
            raise ApiError(400, 'Missing email or password')
        if User.query.filter_by(email=data['email']).first():
            raise ApiError(409, 'User already exists')
        user = User(email=data['email'], password_hash=hash_password(data['password']))
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201

    def patch(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise ApiError(404, 'User not found')
        data = request.json
        if 'password' in data:
            data['password_hash'] = hash_password(data['password'])
            del data['password']

        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                raise ApiError(409, 'Email already in use')

        for key, value in data.items():
            setattr(user, key, value)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ApiError(409, 'Email already in use')

        return jsonify(user.to_dict()), 200

    def delete(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise ApiError(404, 'User not found')
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User and all associated adverts deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/user/email/<email>', methods=['GET'])
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify(user.to_dict()), 200
        else:
            raise ApiError(404, 'User not found')


class AdvertView(MethodView):
    def get(self, advert_id):
        advert = db.session.get(Advert, advert_id)
        if not advert:
            raise ApiError(404, 'Advert not found')
        return jsonify(advert.to_dict())

    @login_required
    def post(self, user):
        data = request.json
        if not data or 'title' not in data or 'description' not in data:
            raise ApiError(400, 'Missing required fields')
        advert = Advert(title=data['title'], description=data['description'], user_id=user.id)
        db.session.add(advert)
        db.session.commit()
        return jsonify(advert.to_dict()), 201

    @login_required
    def patch(self, user, advert_id):
        advert = db.session.get(Advert, advert_id)
        if not advert:
            raise ApiError(404, 'Advert not found')
        if advert.user_id != user.id:
            raise ApiError(403, 'You do not have permission to edit this advert')
        data = request.json
        if not data:
            raise ApiError(400, 'No data provided')
        if 'title' in data:
            advert.title = data['title']
        if 'description' in data:
            advert.description = data['description']
        db.session.commit()
        return jsonify(advert.to_dict()), 200

    @login_required
    def delete(self, user, advert_id):
        advert = db.session.get(Advert, advert_id)
        if not advert:
            raise ApiError(404, 'Advert not found')
        if advert.user_id != user.id:
            raise ApiError(403, 'You do not have permission to delete this advert')
        db.session.delete(advert)
        db.session.commit()
        return jsonify({'status': 'deleted'})


user_view = UserView.as_view('user')
app.add_url_rule('/user/<int:user_id>', view_func=user_view, methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/user', view_func=user_view, methods=['POST'])

advert_view = AdvertView.as_view('advert')
app.add_url_rule('/advert', view_func=advert_view, methods=['POST'])
app.add_url_rule('/advert/<int:advert_id>', view_func=advert_view, methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
