import secrets
from flask import Flask, session, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from models import db


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app)