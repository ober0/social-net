from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    second_name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Integer, default=0)
    date_of_birthday = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    avatar_path = db.Column(db.String(120), nullable=True)
    county = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    education_place = db.Column(db.String(80), nullable=True)
    education_start = db.Column(db.String(80), nullable=True)
    education_end = db.Column(db.String(80), nullable=True)
    show_date_of_birthday = db.Column(db.String(5),  default='True')
    show_gender = db.Column(db.String(5), default='True')
    show_city = db.Column(db.String(5), default='True')
    show_education = db.Column(db.String(5), default='True')
    all_accept = db.Column(db.String(5))
    friends_count = db.Column(db.Integer, default=0)
    subscriptions_count = db.Column(db.Integer, default=0)


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_access = db.Column(db.String(80), nullable=True)
    friend_access = db.Column(db.String(80), nullable=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(80), nullable=True)
    text = db.Column(db.Text, nullable=True)
    href = db.Column(db.String(80), nullable=True)


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    path_name = db.Column(db.String(80), nullable=True)