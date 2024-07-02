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
    city = db.Column(db.String(80), nullable=True)
    education = db.Column(db.String(80), nullable=True)
    show_date_of_birthday = db.Column(db.String(5),  default='True')
    show_gender = db.Column(db.String(5), default='True')
    show_city = db.Column(db.String(5), default='True')
    show_education = db.Column(db.String(5), default='True')