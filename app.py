import base64
import os
import pprint
from functools import wraps
import secrets
from flask import Flask, session, redirect, render_template, request, jsonify, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from flask_mail import Mail, Message
from sqlalchemy import func, and_, or_, text
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Friends, FriendRequest, Notification, Photos, Video, Group, Post, Likes, Warn
from config import app, action_access
import random
import datetime
import imghdr


db.init_app(app)
socketio = SocketIO(app)
mail = Mail(app)


def check_notification(user_id):
    notification = Notification.query.filter_by(user_id=user_id).order_by(Notification.id.desc()).all()
    notification_new = Notification.query.filter_by(user_id=user_id, new=1).all()
    return notification, len(notification_new)



def check_status(action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                status = User.query.filter_by(id=request.cookies.get('account')).first().status
                status_need = action_access[action]

                if status and status_need:
                    if status_need <= status:
                        pass
                    else:
                        return redirect('/')
                else:
                    return redirect('/')

                return f(*args, **kwargs)
            except Exception as e:
                return redirect('/')

        return decorated_function
    return decorator


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



@app.route('/admin/change_status')
@check_status('change_status')
def change_status():
    return render_template('change_status.html')


def createNotification(user_id, type, from_user_avatar_path, text, href, date, from_user, room):
    try:
        new_notification = Notification(user_id=user_id, type=type, from_user_avatar_path=from_user_avatar_path,
                                        text=text,
                                        from_user=from_user, href=href, date=date)
        db.session.add(new_notification)
        db.session.commit()

        socketio.emit('newNotification', {
            'success': True,
            'type': type,
            'user_id': user_id,
            'from_user_avatar_path': from_user_avatar_path,
            'from_user': from_user,
            'date': datetime.datetime.now().strftime('%d.%m.%y в %H:%M'),
            'new': 1,
            'text': text,
            'href': href
        }, room=room)
    except Exception as e:
        db.session.rollback()


@app.route('/')
@check_access
def index():
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = me.avatar_path
    notifications, notifications_count = check_notification(request.cookies.get('account'))
    posts = Post.query.order_by(Post.id.desc()).limit(5).all()
    avatars = []
    authors = []
    _selfs = []
    liked = []
    hrefs = []
    posts_files = []
    for post in posts:
        post_files = []
        if post.isGroup == '1':
            if Group.query.filter_by(id=post.user_id).first().avatar_path:
                avatars.append(f'groups/{Group.query.filter_by(id=post.user_id).first().avatar_path}')
            else:
                avatars.append(f'default.png')

            group_name = Group.query.filter_by(id=post.user_id).first().name
            authors.append(group_name)

            _selfs.append(0)

            if post.images:
                post_images = post.images.split('/')
                for file in post_images:
                    post_files.append(f'group/photos/{file}')

            if post.videos:
                post_videos = post.videos.split('/')
                for file in post_videos:
                    post_files.append(f'group/video/{file}')

            posts_files.append(post_files)
            hrefs.append(f'community/{Group.query.filter_by(id=post.user_id).first().tag}')
        else:
            if User.query.filter_by(id=post.user_id).first().avatar_path:
                avatars.append(f'users/{User.query.filter_by(id=post.user_id).first().avatar_path}')
            else:
                avatars.append(f'default.png')

            username = User.query.filter_by(id=post.user_id).first().name + " " + User.query.filter_by(id=post.user_id).first().second_name
            authors.append(username)

            if int(post.user_id) == int(request.cookies.get('account')):
                _selfs.append(1)
            else:
                _selfs.append(0)

            post_files = []

            if post.images:
                post_images = post.images.split('/')
                for file in post_images:
                    post_files.append(f'users/photos/{file}')

            if post.videos:
                post_videos = post.videos.split('/')
                for file in post_videos:
                    post_files.append(f'users/video/{file}')

            posts_files.append(post_files)

            hrefs.append(f'{User.query.filter_by(id=post.user_id).first().tag}')

        liked_1 = Likes.query.filter_by(user_id=request.cookies.get('account'), post_id=post.id).first()
        if liked_1:
            liked.append(1)
        else:
            liked.append(0)


    return render_template('index.html',
                           username=User.query.filter_by(id=session['account']).first().name,
                           me=me,
                           self_avatar_path=self_avatar_path,
                           notifications=notifications,
                           notification_count=notifications_count,
                           user=User.query.filter_by(id=request.cookies.get('account')).first(),
                           posts=posts,
                           avatars=avatars,
                           authors=authors,
                           _selfs = _selfs,
                           posts_files=posts_files,
                           liked = liked,
                           hrefs = hrefs
                           )


@app.route('/auth', methods=['POST'])
def auth():
    if request.method == "POST":
        for user in User.query.all():
            if str(user.email) == str(request.json.get('email')):
                if check_password_hash(user.password, request.json.get('password')):
                    session['auth'] = True
                    session['account'] = user.id

                    createNotification(user_id=user.id, type='login-to-account', from_user_avatar_path='warn.png',
                                       text=f'Выполнен вход в аккаунт {user.tag} через браузер {request.headers.get("User-Agent")}. Если это были не Вы - смените пароль в ',
                                       from_user='настройках', href='/setting', date=datetime.datetime.now(), room=str(user.id))



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

        return render_template('confirm_email.html', email=email)
    if request.method == "POST":
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
                resp.set_cookie('account', str(session['account']), max_age=60*60*24*14)
                resp.set_cookie('auth', str(session['auth']), max_age=60*60*24*14)
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


@app.route('/addPost', methods=["POST"])
def addPost():
    if request.method == "POST":
        if request.json.get('type') == 'main':
            text = request.json.get('text')
            isPublic = request.json.get('isPublic')
            photos = request.json.get('photos')
            photos_urls = []
            for photo in photos:
                base64_str = photo.split(';base64,')[-1]
                image_binary = base64.b64decode(base64_str)
                photos_url = f'{request.cookies.get("account")} - {secrets.token_hex(16)}.png'
                try:
                    with open(f'static/users/photos/{photos_url}', 'wb') as f:
                        f.write(image_binary)
                    photos_urls.append(photos_url)
                except:
                    return jsonify({'result': False})

            _photos_urls = '/'.join(photos_urls)

            months = {
                '01': 'янв',
                '02': 'фев',
                '03': 'мар',
                '04': 'апр',
                '05': 'май',
                '06': 'июн',
                '07': 'июл',
                '08': 'авг',
                '09': 'сен',
                '10': 'окт',
                '11': 'ноя',
                '12': 'дек'
            }
            time = datetime.datetime.now()
            day = time.strftime('%d')
            month = months[time.strftime('%m')]
            year = time.strftime('%Y')

            date = f'{day} {month} {year}'
            new_post = Post(user_id=request.cookies.get('account'), text=text, images=_photos_urls, date=date)

            try:
                db.session.add(new_post)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'result': False})
            if isPublic:
                if len(photos_urls) > 0:
                    try:
                        for photos_url in photos_urls:
                            newPhoto = Photos(user_id=request.cookies.get('account'), path_name=photos_url, name=f'Фото пользователя {User.query.filter_by(id=request.cookies.get("account")).first().name}')
                            db.session.add(newPhoto)
                        db.session.commit()
                    except:
                        pass

            return jsonify({'result': True})

        elif request.json.get('type') == 'video':
            video = request.json.get('data')

            base64_str = video.split(';base64,')[-1]
            image_binary = base64.b64decode(base64_str)
            video_url = f'{request.cookies.get("account")} - {secrets.token_hex(16)}.mp4'
            try:
                with open(f'static/users/video/{video_url}', 'wb') as f:
                    f.write(image_binary)
            except:
                return jsonify({'result': False})


            last_post = Post.query.filter_by(user_id=request.cookies.get('account')).order_by(Post.id.desc()).first()
            videos = str(last_post.videos)

            if videos != 'None':
                videos = videos + '/' + video_url
            else:
                videos = video_url

            try:
                last_post.videos = videos
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'result': False})


            if request.json.get('isPublic'):
                try:
                    newVideo = Video(user_id=request.cookies.get('account'), path_name=video_url, name=f'Видео пользователя {User.query.filter_by(id=request.cookies.get("account")).first().name}')
                    db.session.add(newVideo)
                    db.session.commit()
                    return jsonify({'result': True})
                except:
                    db.session.rollback()
                    return jsonify({'result': False})


    return jsonify({'result': False})
@app.route('/<string:tag>', methods=['GET'])
def user_profile(tag):
    if request.method == "GET":
        user = User.query.filter_by(tag=tag).first()
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

        video_all = Video.query.filter_by(user_id=request.cookies.get('account')).order_by(Video.id.desc()).all()
        if len(video_all) > 3:
            video = [video_all[i] for i in range(3)]
        else:
            video = [video_all[i] for i in range(len(video_all))]

        friend_count = Friends.query.filter_by(user_id=request.cookies.get('account')).count()

        posts = Post.query.filter_by(user_id=request.cookies.get('account')).order_by(Post.id.desc()).limit(5).all()
        avatars = []
        authors = []
        _selfs = []
        hrefs = []
        liked = []
        posts_files = []
        for post in posts:
            if User.query.filter_by(id=post.user_id).first().avatar_path:
                avatars.append(f'users/{User.query.filter_by(id=post.user_id).first().avatar_path}')
            else:
                avatars.append(f'default.png')

            username = User.query.filter_by(id=post.user_id).first().name + " " + User.query.filter_by(id=post.user_id).first().second_name
            authors.append(username)

            if int(post.user_id) == int(request.cookies.get('account')):
                _selfs.append(1)
            else:
                _selfs.append(0)
            post_files = []

            if post.images:
                post_images = post.images.split('/')
                for file in post_images:
                    post_files.append(f'users/photos/{file}')

            if post.videos:
                post_videos = post.videos.split('/')
                for file in post_videos:
                    post_files.append(f'users/video/{file}')

            posts_files.append(post_files)

            liked_1 = Likes.query.filter_by(user_id=request.cookies.get('account'), post_id=post.id).first()
            if liked_1:
                liked.append(1)
            else:
                liked.append(0)

            hrefs.append(user.tag)
        return render_template('user.html',
                               user=user,
                               _self=_self,
                               _selfs=_selfs,
                               notifications=notifications,
                               notification_count=notifications_count,
                               birthday_correct=birthday_correct,
                               isFriend=isFriend,
                               friends_count=friend_count,
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
                               sec1_video=video,
                               posts=posts,
                               avatars=avatars,
                               authors=authors,
                               posts_files=posts_files,
                               liked=liked,
                               hrefs = hrefs
        )
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/loadMorePosts', methods=['POST'])
def loadMorePosts():
    if request.method == 'POST':
        startWith = request.json.get('startWith')
        all = request.json.get('all')

        if all:
            posts = Post.query.order_by(Post.id.desc()).offset(startWith).limit(5).all()
        else:
            posts = Post.query.filter_by(user_id=request.cookies.get('account')).order_by(Post.id.desc()).offset(
                startWith).limit(5).all()

        usernames = []
        avatars = []
        selfs = []
        tags = []
        texts = []
        files = []
        dates = []
        ids = []
        likes = []
        comments = []
        for post in posts:
            files_1 = []
            if post.text:
                texts.append(post.text)
            else:
                texts.append(None)
            if post.images:
                files_1.extend(post.images.split('/'))
            if post.videos:
                files_1.extend(post.videos.split('/'))
            if not post.images and not post.videos:
                files.append(None)
            else:
                files.append(files_1)
            dates.append(post.date)
            likes.append(post.likes)
            comments.append(post.comments)

            if post.isGroup:
                usernames.append(Group.query.filter_by(id=post.user_id).first().name)
                selfs.append(0)
                tags.append('community/' + Group.query.filter_by(id=post.user_id).first().tag)
                if Group.query.filter_by(id=post.user_id).first().avatar_path:
                    avatars.append('groups/' + Group.query.filter_by(id=post.user_id).first().avatar_path)
                else:
                    avatars.append('default.png')
            else:
                usernames.append(f"{User.query.filter_by(id=request.cookies.get('account')).first().name} {User.query.filter_by(id=post.user_id).first().second_name}")
                if post.user_id == int(request.cookies.get('account')):
                    selfs.append(1)
                else:
                    selfs.append(0)
                tags.append(User.query.filter_by(id=post.user_id).first().tag)
                if User.query.filter_by(id=post.user_id).first().avatar_path:
                    avatars.append('users/' + User.query.filter_by(id=post.user_id).first().avatar_path)
                else:
                    avatars.append('default.png')

            ids.append(post.id)
        posts_json = {
            'success': True,
            'usernames': usernames,
            'avatars': avatars,
            'text': texts,
            'files': files,
            'dates': dates,
            'likes': likes,
            'comments': comments,
            'href': tags,
            'selfs': selfs,
            'ids': ids
        }

        if posts:
            return jsonify(posts_json)
        else:
            return jsonify({'success': False})
    return 'Страница не найдена'

@app.route('/removePost', methods=['POST'])
def removePost():
    if request.method == 'POST':
        post_id = int(request.json.get('id'))

        try:
            post = Post.query.filter_by(id=post_id).first()
            if post:
                if int(request.cookies.get('account')) == post.user_id and not post.isGroup:
                    db.session.delete(post)
                    db.session.commit()
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False})
            return jsonify({'success': False})

        except:
            return jsonify({'success': False})
    else:
        return 'Страница не найдена'


@app.route('/notificationView', methods=["POST"])
def notificationView():
    if request.method == "POST":
        id = request.cookies.get('account')
        notifications = Notification.query.filter_by(user_id=id, new=1).all()
        for notification in notifications:
            notification.new = 0
            db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/notificationDelete', methods=["POST"])
def notificationDelete():
    if request.method == "POST":
        id = request.cookies.get('account')
        notifi_to_del = request.json.get('notifi')
        if notifi_to_del:
            if notifi_to_del == 'all':
                try:
                    notifications = Notification.query.filter_by(user_id=id, new=0).all()
                    for notification in notifications:
                        db.session.delete(notification)
                    db.session.commit()
                    return jsonify({'success': True})
                except Exception as e:
                    return jsonify({'success': False})
            else:
                notification = Notification.query.filter_by(user_id=id, id=int(notifi_to_del)).first()
                if notification:
                    try:
                        db.session.delete(notification)
                        db.session.commit()
                        return jsonify({'success': True})
                    except Exception as e:
                        return jsonify({'success': False})
                return jsonify({'success': False})

        return jsonify({'success': False})
    return jsonify({'success': False})


@socketio.on('edit_profile_save')
def edit_profile_save(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    try:
        user_id = request.cookies.get('account')
        user = User.query.filter_by(id=user_id, tag=data['tag']).first()

        if user:
            date_of_birth = datetime.datetime.strptime(data['birthday'], '%Y-%m-%d').date()

            try:
                avatar = data['file']

                if avatar:
                    image_type = imghdr.what(None, h=avatar)
                    filename = f'avatar-user-{request.cookies.get("account")}.{image_type}'

                    for i in os.listdir('static/avatars/users'):
                        if i.startswith("avatar-user-1"):
                            file_path = os.path.join('static/avatars/users', i)
                            os.remove(file_path)

                    with open(f'static/avatars/users/{filename}', 'wb') as f:
                        f.write(avatar)
                    user.avatar_path = filename
            except Exception as e:
                pass

            user.name = data['name'].title()
            user.second_name = data['second_name'].title()
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
            socketio.emit('edit_profile_save_result', {'result': True, 'tag':tag},room=request.cookies.get('account'))
        else:
            data = {
                'result': False,
                'error': 'Пользователь не найден: ошибка доступа'
            }
            socketio.emit('edit_profile_save_result', data, room=request.cookies.get('account'))
    except Exception as e:
        error_message = str(e)
        data = {
            'result': False,
            'error': error_message
        }
        socketio.emit('edit_profile_save_result', data, room=request.cookies.get('account'))


@socketio.on('addFriend_request')
def add_friend(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    user_id = request.cookies.get('account')
    friend_id = data['friend_id']

    try:
        me = User.query.filter_by(id=user_id).first()

        friend_requests = FriendRequest(user_id=user_id, friend_id=friend_id, user_access='yes')
        db.session.add(friend_requests)
        db.session.commit()

        from_avatar = User.query.filter_by(id=user_id).first().avatar_path
        user_name = User.query.filter_by(id=user_id).first().name + " " + User.query.filter_by(id=user_id).first().second_name

        createNotification(user_id=friend_id, type='newFriendRequest', from_user_avatar_path=from_avatar,
                           text=f'Новое предложение дружбы от',
                           from_user=user_name, href=f'/{me.tag}', date=datetime.datetime.now(), room=friend_id)

        socketio.emit('addFriend_request_result', {'success': True}, room=request.cookies.get('account'))

    except Exception as e:
        db.session.rollback()
        socketio.emit('addFriend_request_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))

@socketio.on('removeFriend')
def add_friend(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    user_id = request.cookies.get('account')
    friend_id = data['friend_id']

    try:
        friend1 = Friends.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
        friend2 = Friends.query.filter_by(user_id=friend_id).filter_by(friend_id=user_id).first()

        db.session.delete(friend1)
        db.session.delete(friend2)
        db.session.commit()
        socketio.emit('removeFriend_result', {'success': True}, room=request.cookies.get('account'))
    except Exception as e:
        db.session.rollback()
        socketio.emit('removeFriend_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))


@socketio.on('removeFriend_request')
def remove_friend_request(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    user_id = data['user_id']
    friend_id = data['friend_id']

    request1 = FriendRequest.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
    try:
        db.session.delete(request1)
        db.session.commit()
        socketio.emit('removeFriend_request_result', {'success': True}, room=request.cookies.get('account'))
    except Exception as e:
        db.session.rollback()
        socketio.emit('removeFriend_request_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))



@socketio.on('addFriend')
def add_friend(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    friend_id = data['friend_id']
    user_id = data['user_id']

    request1 = FriendRequest.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
    request1.friend_access = 'yes'
    db.session.commit()

    if request1.friend_access == 'yes' and request1.user_access == 'yes':
        db.session.delete(request1)
        db.session.commit()

        try:
            new_friend1 = Friends(user_id=user_id, friend_id=friend_id)
            new_friend2 = Friends(user_id=friend_id, friend_id=user_id)

            db.session.add(new_friend1)
            db.session.add(new_friend2)
            db.session.commit()
            socketio.emit('addFriend_result', {'success': True}, room=request.cookies.get('account'))
        except Exception as e:
            db.session.rollback()
            socketio.emit('addFriend_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))

        try:
            notif_to_rem = Notification.query.filter_by(user_id=friend_id).filter_by(type='newFriendRequest').all()
            for notif in notif_to_rem:
                db.session.delete(notif)
                db.session.commit()
        except:
            db.session.rollback()



@socketio.on('newPhoto')
def new_photo(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    user_id = request.cookies.get('account')
    file = data['file']
    filename = data['filename']
    if file:
        socketio.emit('newPhoto_result', {'success': True}, room=request.cookies.get('account'))
    else:
        socketio.emit('newPhoto_result', {'success': False, 'error': 'Файл не найден'}, room=request.cookies.get('account'))




@socketio.on('newPhotos_all')
def new_photos_res(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
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
                socketio.emit('newPhoto_all_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))
                return False
        socketio.emit('newPhoto_all_result', {'success': True}, room=request.cookies.get('account'))
    except Exception as e:
        socketio.emit('newPhoto_all_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))



@socketio.on('deletePhoto')
def delete_photo(data):
    photo_id = data['photo_id']
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    photo = Photos.query.filter_by(id=photo_id).first()

    if photo:
        try:
            db.session.delete(photo)
            db.session.commit()
            os.remove(f'static/users/photos/{photo.path_name}')
            socketio.emit('deletePhoto_result', {'success': True}, room=request.cookies.get('account'))

        except Exception as e:
            db.session.rollback()
            socketio.emit('deletePhoto_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))
    else:
        socketio.emit('deletePhoto_result', {'success': False, 'error': ' Фото не найдено, обратитесь в поддержку'}, room=request.cookies.get('account'))



@app.route('/deleteVideo', methods=['POST'])
def delete_video():

    video_id = request.json.get('video_id')

    video = Video.query.filter_by(id=video_id).first()

    if video:
        try:
            db.session.delete(video)
            db.session.commit()
            return jsonify({'success': True})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})

        os.remove(f'static/users/video/{video.path_name}')
    else:
        return jsonify({'success': False, 'error': ' Фото не найдено, обратитесь в поддержку'})



@socketio.on('find_user_tag')
def find_user_tag(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    tag = data['tag']
    user = User.query.filter_by(tag=tag).first()
    if user:
        socketio.emit('find_user_tag_result', {'success': True, 'user_name':f'{user.name} {user.second_name}', 'user_email': user.email, 'user_tag': tag, 'user_status': str(user.status)}, room=request.cookies.get('account'))
    else:
        socketio.emit('find_user_tag_result', {'success': False}, room=request.cookies.get('account'))

@socketio.on('updateStatus')
def update_status(data):
    join_room(request.cookies.get('account'), request.cookies.get('user_id'))
    tag = data['tag']
    status = int(data['status'])
    user = User.query.filter_by(tag=tag).first()
    if user:
        user.status = status
        db.session.commit()
        socketio.emit('updateStatus_result', {'success': True}, room=request.cookies.get('account'))
    else:
        socketio.emit('updateStatus_result', {'success': False}, room=request.cookies.get('account'))


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        data = request.json.get('data')
        if data:
            users_result = []
            groups_result = []
            group_tag = ''
            search_string = f"%{data}%"

            # Поиск тэга
            user = User.query.filter(User.tag.like(search_string)).first()
            if user:
                users_result.append(user)

            # Поиск по имени и фамилии
            for search_string in [search_string, search_string.title()]:
                users = User.query.filter(or_(
                    User.name.like(search_string),
                    User.second_name.like(search_string),
                    text(f"({User.name} || ' ' || {User.second_name}) LIKE :search_string")
                )).params(search_string=search_string).all()

            if users:
                users_result.extend(users)

            # Поиск группы по тегу
            group = Group.query.filter(Group.tag.like(search_string)).first()
            if group:
                group_tag = group
                groups_result.append(group)

            # Поиск группы по названию
            groups = Group.query.filter(Group.name.like(search_string)).all()
            if groups:
                for group in groups:
                    if group != group_tag:
                        groups_result.append(group)

            user_names = [user.name for user in users_result]
            user_second_names = [user.second_name for user in users_result]

            user_city = []
            for user in users_result:
                if user.show_city == '1':
                    user_city.append(user.city)
                else:
                    user_city.append(' ')
            user_avatar_paths = []
            for user in users_result:
                if user.avatar_path:
                    user_avatar_paths.append(user.avatar_path)

            user_avatar_paths = [user.avatar_path for user in users_result]
            user_tags = [user.tag for user in users_result]

            group_names = [group.name for group in groups_result]
            group_tags = [group.tag for group in groups_result]

            group_avatar_paths = []
            for group in groups_result:
                if group.avatar_path:
                    group_avatar_paths.append(group.avatar_path)
            group_subscribers = []
            for group in groups_result:
                if group.subscribers:
                    group_subscribers.append(group.subscribers)
                else:
                    group_subscribers.append('0')
            search_results = {
                'success': True,
                'users': {
                    'names': user_names,
                    'second_names': user_second_names,
                    'city': user_city,
                    'avatar_paths': user_avatar_paths,
                    'user_tags': user_tags
                },
                'groups': {
                    'names': group_names,
                    'tags': group_tags,
                    'avatar_paths': group_avatar_paths,
                    'subscribers': group_subscribers
                }
            }

            return jsonify(search_results)
        else:
            return jsonify({'success': False})


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
