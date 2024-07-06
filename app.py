import base64
import os
from functools import wraps
import secrets
from flask import Flask, session, redirect, render_template, request, jsonify, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Friends, FriendRequest, Notification, Photos
from config import app
import random
import datetime
import imghdr


db.init_app(app)
socketio = SocketIO(app)
mail = Mail(app)


def check_notification(user_id):
    notification = Notification.query.filter_by(user_id=user_id).all()
    print(len(notification))
    return notification, len(notification)


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
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = me.avatar_path
    notifications, notifications_count = check_notification(request.cookies.get('account'))
    return render_template('index.html', username=User.query.filter_by(id=session['account']).first().name, me=me, self_avatar_path=self_avatar_path, notifications=notifications, notification_count=notifications_count)


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
                    resp.set_cookie('account', str(session['account']), max_age=60*60*24*14)
                    resp.set_cookie('auth', str(session['auth']), max_age=60*60*24*14)
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
        print(session['auth_code'])

        return render_template('confirm_email.html', email=email)
    if request.method == "POST":
        code = request.json
        print(code)
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
                print(3)
                session['auth_code'] = ''

                resp = make_response(jsonify({
                    'res': True
                }), 200)
                resp.set_cookie('account', str(session['account']), max_age=60*60*24*14)
                resp.set_cookie('auth', str(session['auth']), max_age=60*60*24*14)
                return resp

            except Exception as e:
                db.session.rollback()
        print(1, session['auth_code'])
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
def user_profile(tag):
    if request.method == "GET":
        user = User.query.filter_by(tag=tag).first()
        print(user)
        self_user_tag = User.query.filter_by(id=request.cookies.get('account')).first().tag

        notifications, notifications_count = check_notification(request.cookies.get('account'))

        month_data = {
            '1': 'января',
            '2': 'февраля',
            '3': 'марта',
            '4': 'апреля',
            '5': 'мая',
            '6': 'июня',
            '7': 'июля',
            '8': 'августа',
            '9': 'сентября',
            '10': 'октября',
            '11': 'ноября',
            '12': 'декабря'
        }


        birthday = str(user.date_of_birthday)
        birthday_list = birthday.split('-')
        day = birthday_list[2]
        month = month_data[birthday_list[1]]
        year = birthday_list[0]

        birthday_correct = f'{day} {month} {year}'

        _self = 1 if self_user_tag == tag else 0
        friends = Friends.query.filter_by(user_id=request.cookies.get('account')).all()
        isFriend = 0
        for friend in friends:
            if friend.friend_id == user.id:
                isFriend = 1

        friend_request_from_user = 1 if FriendRequest.query.filter_by(user_id=request.cookies.get('account')).filter_by(friend_id=user.id).first() else 0
        friend_request = 1 if FriendRequest.query.filter_by(user_id=user.id).filter_by(friend_id=request.cookies.get('account')).first() else 0

        me = User.query.filter_by(id=request.cookies.get('account')).first()
        self_avatar_path = me.avatar_path

        sec1_all_photos = Photos.query.filter_by(user_id=user.id).order_by(Photos.id.desc()).all()

        if len(sec1_all_photos) > 8:
            sec1_photos = [sec1_all_photos[i] for i in range(8)]
        else:
            sec1_photos = [sec1_all_photos[i] for i in range(len(sec1_all_photos))]
        return render_template('user.html',
                               user=user,
                               _self=_self,
                               notifications=notifications,
                               notification_count=notifications_count,
                               birthday_correct=birthday_correct,
                               isFriend=isFriend,
                               self_avatar_path=self_avatar_path,
                               me=me,
                               friend_request_from_user=friend_request_from_user,
                               friend_request=friend_request,
                               sec1_photos=sec1_photos,
                               sec1_music=[
                                   {'id': 1, 'path_name': '1.png', 'name': 'Песня 1', 'autor': 'Исполнитель 1'},
                                   {'id': 2, 'path_name': '2.png', 'name': 'Песня 2', 'autor': 'Исполнитель 2'},
                                   {'id': 3, 'path_name': '3.png', 'name': 'Песня 3', 'autor': 'Исполнитель 3'},
                                   {'id': 4, 'path_name': '4.png', 'name': 'Песня 4', 'autor': 'Исполнитель 4'},
                                   {'id': 1, 'path_name': '1.png', 'name': 'Песня 1', 'autor': 'Исполнитель 1'},
                                   {'id': 2, 'path_name': '2.png', 'name': 'Песня 2', 'autor': 'Исполнитель 2'},
                                   {'id': 3, 'path_name': '3.png', 'name': 'Песня 3', 'autor': 'Исполнитель 3'},
                                   {'id': 4, 'path_name': '4.png', 'name': 'Песня 4', 'autor': 'Исполнитель 4'},
                                   {'id': 4, 'path_name': '4.png', 'name': 'Песня 4', 'autor': 'Исполнитель 4'}
                               ],
                               sec1_video=[
                                   {'id': 1, 'path_name': '1.mkv'},
                                   {'id': 1, 'path_name': '1.mkv'},
                                   {'id': 1, 'path_name': '1.mkv'},
                               ],
        )
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


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
            tag = user.tag
            socketio.emit('edit_profile_save_result', {'result': True, 'tag':tag})
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


@socketio.on('addFriend_request')
def add_friend(data):
    user_id = request.cookies.get('account')
    friend_id = data['friend_id']
    friend = User.query.filter_by(id=friend_id).first()
    try:

        friend_requests = FriendRequest(user_id=user_id, friend_id=friend_id, user_access='yes')
        db.session.add(friend_requests)
        db.session.commit()

        newNotification = Notification(type='newFriendRequest', user_id=friend_id, text=f'Новое предложение дружбы от {friend.name} {friend.second_name}', href=f'/{friend.tag}')
        db.session.add(newNotification)
        db.session.commit()
        socketio.emit('addFriend_request_result', {'success': True})

    except Exception as e:
        db.session.rollback()
        socketio.emit('addFriend_request_result', {'success': False, 'error': str(e)} )

@socketio.on('removeFriend')
def add_friend(data):
    user_id = request.cookies.get('account')
    friend_id = data['friend_id']

    try:
        friend1 = Friends.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
        friend2 = Friends.query.filter_by(user_id=friend_id).filter_by(friend_id=user_id).first()

        db.session.delete(friend1)
        db.session.delete(friend2)
        db.session.commit()
        socketio.emit('removeFriend_result', {'success': True})
    except Exception as e:
        db.session.rollback()
        socketio.emit('removeFriend_result', {'success': False, 'error': str(e)})


@socketio.on('removeFriend_request')
def remove_friend_request(data):
    user_id = data['user_id']
    friend_id = data['friend_id']

    request = FriendRequest.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
    try:
        db.session.delete(request)
        db.session.commit()
        socketio.emit('removeFriend_request_result', {'success': True})
    except Exception as e:
        db.session.rollback()
        socketio.emit('removeFriend_request_result', {'success': False, 'error': str(e)})



@socketio.on('addFriend')
def add_friend(data):
    friend_id = data['friend_id']
    user_id = data['user_id']

    request = FriendRequest.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
    request.friend_access = 'yes'
    db.session.commit()

    if request.friend_access == 'yes' and request.user_access == 'yes':
        db.session.delete(request)
        db.session.commit()

        try:
            new_friend1 = Friends(user_id=user_id, friend_id=friend_id)
            new_friend2 = Friends(user_id=friend_id, friend_id=user_id)

            db.session.add(new_friend1)
            db.session.add(new_friend2)
            db.session.commit()
            socketio.emit('addFriend_result', {'success': True})
        except Exception as e:
            db.session.rollback()
            socketio.emit('addFriend_result', {'success': False, 'error': str(e)})




@socketio.on('newPhoto')
def new_photo(data):
    user_id = request.cookies.get('account')
    file = data['file']
    filename = data['filename']
    print(1)
    if file:
        socketio.emit('newPhoto_result', {'success': True})
        # try:
        #     with open(f'static/users/photos/user{user_id}uniq{secrets.token_hex(8)}-{filename}', 'wb') as f:
        #         f.write(file)
        #     new_photo = Photos(user_id=user_id, name=filename, path_name=f'user{user_id}-{filename}')
        #     db.session.add(new_photo)
        #     db.session.commit()
        #     socketio.emit('newPhoto_result', {'success': True})
        # except Exception as e:
        #     db.session.rollback()
        #     socketio.emit('newPhoto_result', {'success': False, 'error': str(e)})
    else:
        socketio.emit('newPhoto_result', {'success': False, 'error': 'Файл не найден'})



@socketio.on('newPhotos_all')
def new_photos_res(data):
    files = data['files']
    filenames = data['filenames']
    user_id = request.cookies.get('account')
    try:
        for i in range(len(files)):
            file = files[i]
            _, encoded_data = file.split(',', 1)
            image_data = base64.b64decode(encoded_data)
            try:
                name = f'user{user_id}uniq{secrets.token_hex(8)}-{filenames[i]}'
                with open(f'static/users/photos/{name}','wb') as f:
                    f.write(image_data)
                new_photo = Photos(user_id=user_id, name=filenames[i], path_name=f'{name}')
                db.session.add(new_photo)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                socketio.emit('newPhoto_all_result', {'success': False, 'error': str(e)})
                return False
        socketio.emit('newPhoto_all_result', {'success': True})
    except Exception as e:
        socketio.emit('newPhoto_all_result', {'success': False, 'error': str(e)})

@socketio.on('join_main_room')
def join_room_handle(data):
    account = request.cookies.get('account')
    join_room(account)

@socketio.on('disconnect')
def disconnect():
    leave_room(request.cookies.get('account'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, allow_unsafe_werkzeug=True)
