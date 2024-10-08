from datetime import datetime

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



class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    avatar_path = db.Column(db.String(120))
    tag = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subscribers = db.Column(db.Integer, default=0)

class Subscribe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))


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
    from_user = db.Column(db.String(80), nullable=True)
    from_user_avatar_path = db.Column(db.String(120), nullable=True)
    text = db.Column(db.Text, nullable=True)
    href = db.Column(db.String(80), nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    new = db.Column(db.Integer, default=1)


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    path_name = db.Column(db.String(80), nullable=True, unique=True)
    inPost = db.Column(db.String(10), default='False')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    path_name = db.Column(db.String(80), nullable=True, unique=True)
    inPost = db.Column(db.String(10), default='False')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,  nullable=False)
    isGroup = db.Column(db.String(10), nullable='0')
    text = db.Column(db.Text, nullable=True)
    images = db.Column(db.Text, nullable=True)
    videos = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(100), nullable=True)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    text = db.Column(db.Text, nullable=True)
    time = db.Column(db.String(100), nullable=True)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    notification_friend_request = db.Column(db.Integer, default=1)
    notification_friend_access = db.Column(db.Integer, default=1)
    notification_message = db.Column(db.Integer, default=1)
    notification_friend_posts = db.Column(db.Integer, default=1)
    notification_community_posts = db.Column(db.Integer, default=1)
    profile_open = db.Column(db.Integer, default=1)


class TechnicalSupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_phone = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(80), default='Открыт')
    theme = db.Column(db.String(80), nullable=False)
    info = db.Column(db.Text, nullable=False)

class Chats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_message = db.Column(db.String(80), nullable=True)
    last_message_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=True)
    time = db.Column(db.String(100), nullable=True)

