import os
from functools import wraps
import secrets
from flask import Flask, session, redirect, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User  # Предполагается, что у вас есть модуль models с описанием базы данных
from config import app
import random
import datetime
import imghdr

# Инициализация приложения, базы данных и Socket.IO
db.init_app(app)
socketio = SocketIO(app)
mail = Mail(app)


def check_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if request.cookies.get('auth') == 'True':
                session['auth'] = True
            else:
                session['auth'] = False
            session['account'] = int(request.cookies.get('account'))
        except:
            pass

        if 'auth' not in session or not session['auth']:
            session['auth_data'] = ''
            session['auth_code'] = ''
            emails = [user.email for user in User.query.all()]
            return render_template('auth.html', emails=emails)

        user = User.query.filter_by(id=session.get('account')).first()
        if not user:
            emails = [user.email for user in User.query.all()]
            return render_template('auth.html', emails=emails)
        elif not user.name:
            return redirect('/edit_user')

        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@check_access
def index():
    return render_template('index.html', username=User.query.filter_by(id=session['account']).first().name)


@app.route('/auth', methods=['POST'])
def auth():
    if request.method == "POST":
        for user in User.query.all():
            if str(user.email) == str(request.json.get('email')):
                if check_password_hash(user.password, request.json.get('password')):
                    session['auth'] = True
                    session['account'] = user.id
                    resp = make_response(jsonify({
                        'result': True
                    }), 200)
                    resp.set_cookie('account', str(session['account']))
                    resp.set_cookie('auth', str(session['auth']))
                    return resp
        return jsonify({
            'result': False
        }), 401


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == "GET":
        if session.get('auth') == True:
            return redirect('/')
        else:
            return render_template('reg.html', emails=[user.email for user in User.query.all()])

    if request.method == "POST":
        tag = request.json.get('tag')
        email = request.json.get('email')
        password = request.json.get('password')

        hashed_password = generate_password_hash(password)

        session['auth_data'] = f'{tag}:%:%:{email}:%:%:{hashed_password}'
        if email not in [i.email for i in User.query.all()]:
            return jsonify({
                'result': True
            }), 200

        return jsonify({
            'result': False
        }), 401


@app.route('/confirm_email', methods=['GET', 'POST'])
def confirm_email():
    if request.method == "GET":
        data = session.get('auth_data').split(':%:%:')
        email = data[1]
        code = random.randint(100000, 999999)
        msg = Message('Код подтверждения', recipients=[email])
        with open('templates/send.html', 'r', encoding='utf-8') as f:
            text = f.read()
            textSplit = text.split('//////')
            textSplit.append(textSplit[1])
            textSplit[1] = str(code)
            result = ''.join(textSplit)
        msg.html = result
        mail.send(msg)
        session['auth_code'] = code

        return render_template('confirm_email.html', email=email)
    else:
        code = request.json
        if str(code) == str(session['auth_code']):
            data = session.get('auth_data').split(':%:%:')
            hashed_password = data[2]
            user = User(tag=data[0], email=data[1], password=hashed_password, status=0)
            try:
                db.session.add(user)
                db.session.commit()

                session['auth'] = True
                session['account'] = user.id
                session['auth_data'] = ''
                session['auth_code'] = ''

                resp = make_response(jsonify({
                    'res': True
                }), 200)
                resp.set_cookie('account', str(session['account']))
                resp.set_cookie('auth', str(session['auth']))
                return resp

            except Exception as e:
                db.session.rollback()

        return jsonify({
            'res': False
        }), 401


@app.route('/exit')
@check_access
def exit():
    session['auth'] = False
    session['account'] = ''

    resp = make_response(redirect('/'))
    resp.set_cookie('account', '')
    resp.set_cookie('auth', 'False')
    return resp


@app.route('/checkUniqueTag', methods=["POST"])
def checkUniqueTag():
    if request.method == "POST":
        tag = request.json.get('tag')
        if not User.query.filter(User.id != request.cookies.get('account')).filter_by(tag=tag).first():
            return jsonify({'result': True})
        else:
            return jsonify({'result': False})
    else:
        return 'Страницы не существует'


@app.route('/edit_user', methods=["POST", "GET"])
def edit_user():
    if request.method == "POST":
        pass
    if request.method == "GET":
        user = User.query.filter_by(id=request.cookies.get('account')).first()
        if user:
            return render_template('edit_user.html', user=user)
        else:
            return 'Страница не найдена'

@app.route('/<string:tag>', methods=['GET'])
@check_access
def user_profile(tag):
    if request.method == "GET":
        user = User.query.filter_by(tag=tag).first()
        self_user_tag = User.query.filter_by(id=request.cookies.get('account')).first().tag
        notification_count = 1

        return render_template('user.html', user=user, self=(self_user_tag == tag), notification_count=notification_count)


@socketio.on('edit_profile_save')
def edit_profile_save(data):
    try:
        user_id = request.cookies.get('account')
        user = User.query.filter_by(id=user_id, tag=data['tag']).first()

        if user:
            date_of_birth = datetime.datetime.strptime(data['birthday'], '%Y-%m-%d').date()

            try:
                avatar = data['file']

                if avatar:
                    image_type = imghdr.what(None, h=avatar)
                    print(image_type)
                    filename = f'avatar-user-{request.cookies.get("account")}.{image_type}'

                    for i in os.listdir('static/avatars/users'):
                        if i.startswith("avatar-user-1"):
                            file_path = os.path.join('static/avatars/users', i)
                            os.remove(file_path)

                    with open(f'static/avatars/users/{filename}', 'wb') as f:
                        f.write(avatar)
                    user.avatar_path = filename
            except Exception as e:
                print(e)

            user.name = data['name']
            user.second_name = data['second_name']
            user.tag = data['tag']
            user.gender = data['gender']
            user.date_of_birthday = date_of_birth
            user.county = data['country']
            user.city = data['city']
            user.education_place = data['education_place']
            user.education_start = data['education_start']
            user.education_end = data['education_end']
            user.show_date_of_birthday = data['show_birthday']
            user.show_gender = data['show_gender']
            user.show_education = data['show_education']
            user.show_city = data['show_address']
            user.all_accept = 'yes'


            db.session.commit()
            socketio.emit('edit_profile_save_result', {'result': True})
        else:
            data = {
                'result': False,
                'error': 'Пользователь не найден: ошибка доступа'
            }
            socketio.emit('edit_profile_save_result', data)
    except Exception as e:
        error_message = str(e)
        print(error_message)
        data = {
            'result': False,
            'error': error_message
        }
        socketio.emit('edit_profile_save_result', data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, allow_unsafe_werkzeug=True)
