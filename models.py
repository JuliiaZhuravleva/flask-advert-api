from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    adverts = db.relationship('Advert', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }


class Advert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date.isoformat(),
            'owner': self.owner.to_dict()
        }
