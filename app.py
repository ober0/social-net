import base64
import logging
import os
import pprint
from functools import wraps
import secrets
from flask import Flask, session, redirect, render_template, request, jsonify, make_response, send_from_directory
from flask.json import tag
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from flask_mail import Mail, Message
from sqlalchemy import func, and_, or_, text
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Friends, FriendRequest, Notification, Photos, Video, Group, Post, Likes, Comments, \
    Subscribe
from config import app, action_access, month_data
import random
import datetime
import imghdr


db.init_app(app)
socketio = SocketIO(app)
mail = Mail(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Получение уведомлений и количества новых уведомлений
def check_notification(user_id):
    notification = Notification.query.filter_by(user_id=user_id).order_by(Notification.id.desc()).all()
    notification_new = Notification.query.filter_by(user_id=user_id, new=1).all()
    return notification, len(notification_new)


#Проверка на код доступа
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


#Проверка на вход в аккаунт
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



('/admin/change_status')
@check_status('change_status')
def change_status():
    return render_template('change_status.html')

@app.route('/comments/add', methods=['POST'])
def add_comment():
    comment = request.json.get('comment')
    post_id = request.json.get('post_id')
    time = datetime.datetime.now().strftime('%d.%m.%Y в %H:%M')
    new_comment = Comments(text=comment, post_id=post_id, user_id=request.cookies.get('account'), time=time)
    try:
        db.session.add(new_comment)

        post = Post.query.filter_by(id=post_id).first()
        post.comments += 1

        db.session.commit()

        user = User.query.filter_by(id=request.cookies.get('account')).first()
        username = user.name + " " + user.second_name
        data = {
            'success': True,
            'usernames': [username],
            'avatars': [user.avatar_path],
            'texts': [comment],
            'times': [datetime.datetime.now().strftime('%d.%m.%y в %H:%M')],
            'selfs': [True],
            'hrefs': ['/' + user.tag],
            'ids': [new_comment.id]
        }
        

        return jsonify(data)

    except:
        db.session.rollback()
        return jsonify({'success': False})





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

    section = request.args.get('section')
    if not section:
        section = 'new'

    incoming_requests_count = FriendRequest.query.filter_by(friend_id=me.id).count()
    return render_template('index.html',
                           username=User.query.filter_by(id=session['account']).first().name,
                           me=me,
                           self_avatar_path=self_avatar_path,
                           notifications=notifications,
                           notification_count=notifications_count,
                           user=User.query.filter_by(id=request.cookies.get('account')).first(),
                           section=section,
                           incoming_requests_count = incoming_requests_count
                           )



@app.route('/groups')
@check_access
def groops():
    user_tag = request.args.get('user')
    user = User.query.filter_by(tag=user_tag).first()

    groops_subs = Subscribe.query.filter_by(user_id=user.id).limit(15).all()
    groops_data_count = Subscribe.query.filter_by(user_id=user.id).count()

    groops_ids = [i.group_id for i in groops_subs]

    groops = Group.query.filter(Group.id.in_(groops_ids)).all()




    titles = []
    hrefs = []
    tags = []
    avatar_paths = []
    subscribers = []

    for group in groops:
        titles.append(group.name)
        hrefs.append(f'/community/{group.tag}')
        tags.append(group.tag)
        avatar_path = group.avatar_path
        if not avatar_path:
            avatar_path = 'default.png'
        else:
            avatar_path = f'groups/{group.avatar_path}'
        avatar_paths.append(avatar_path)
        if group.subscribers:
            subscribers.append(group.subscribers)
        else:
            subscribers.append(0)
    groops_data = {
        'titles': titles,
        'hrefs': hrefs,
        'tags': tags,
        'avatar_paths': avatar_paths,
        'subscribers': subscribers
    }

    _self = (str(user.id) == request.cookies.get('account'))

    notifications, notifications_count = check_notification(request.cookies.get('account'))

    incoming_requests = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).order_by(
        FriendRequest.id.desc()).all()

    return render_template('user-groops.html',
                           groops_data=groops_data,
                           _self=_self,
                           groops_data_count=groops_data_count,
                           me=User.query.filter_by(id=request.cookies.get('account')).first(),
                           user=User.query.filter_by(id=request.cookies.get('account')).first(),
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path = User.query.filter_by(id=request.cookies.get('account')).first().avatar_path,
                           incoming_requests_count=len(incoming_requests),
                           )



@app.route('/groups/load-more', methods=['POST'])
def load_more():
    offset = request.json.get('count')
    user_tag = request.json.get('user_tag')
    user = User.query.filter_by(tag=user_tag).first()

    filter = request.args.get('filter')

    try:
        if not filter:

             subscribers = Subscribe.query.filter_by(user_id=user.id).order_by(Subscribe.id.desc()).offset(offset).limit(15).all()
        else:

            search_string = f"%{filter}%"
            print(search_string)
            for search_string in [search_string, search_string.title()]:
                groups = Group.query.filter(Group.name.like(search_string)).all()
            group_ids = [group.id for group in groups]

            groups = User.query.filter(User.tag.like(search_string)).all()
            groups_ids2 = [group.id for group in groups]

            group_ids.extend(groups_ids2)

            subscribers = Subscribe.query.filter_by(user_id=user.id).filter(Subscribe.group_id.in_(group_ids)).limit(50).all()

            print(subscribers)
        names = []
        subs = []
        avatar_paths = []
        hrefs = []
        tags = []

        for group in subscribers:
            friend_data = Group.query.filter_by(id=group.group_id).first()
            names.append(friend_data.name)
            if friend_data.subscribers:
                subs.append(friend_data.subscribers)
            else:
                subs.append(0)
            avatar_path = friend_data.avatar_path
            if not avatar_path:
                avatar_path = 'default.png'
            else:
                avatar_path = f'users/{avatar_path}'
            avatar_paths.append(avatar_path)
            hrefs.append('/community/' + friend_data.tag)
            tags.append(friend_data.tag)
        _self = (str(User.query.filter_by(tag=user_tag).first().id) == request.cookies.get('account'))
        friends_data = {
            'success': True,
            'title': names,
            'subs': subs,
            'avatar_paths': avatar_paths,
            'hrefs': hrefs,
            'tags': tags,
            'self': _self
        }
        return jsonify(friends_data)
    except Exception as e:
        return jsonify({'success': False})




@app.route('/groups/unsubscribe', methods=['POST'])
def unsubscribe():
    group_tag = request.json.get('tag')
    self_id = request.cookies.get('account')
    group_id = Group.query.filter_by(tag=group_tag).first().id

    unsubscribe = Subscribe.query.filter_by(user_id=self_id, group_id=group_id).first()
    try:
        User.query.filter_by(id=self_id).first().subscriptions_count -= 1

        db.session.delete(unsubscribe)
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False})


@app.route('/friends')
@check_access
def friends():
    section = request.args.get('section')
    if not section:
        section = 'friends'

    tag = request.args.get('user')
    user = User.query.filter_by(tag=tag).first()
    _self = (tag == User.query.filter_by(id=request.cookies.get('account')).first().tag)

    friends = Friends.query.filter_by(user_id=user.id).order_by(Friends.id.desc()).limit(15).all()
    friends_count = len(Friends.query.filter_by(user_id=user.id).order_by(Friends.id.desc()).all())

    friend_names = []
    friend_learn = []
    friend_avatar_path = []
    friend_hrefs = []
    friend_tags = []
    for friend in friends:
        friend_data = User.query.filter_by(id=friend.friend_id).first()

        friend_names.append(f'{friend_data.name} {friend_data.second_name}')
        if friend_data.show_education == '1':
            friend_learn.append(friend_data.education_place)
        else:
            friend_learn.append(None)
        avatar_path = friend_data.avatar_path
        if not avatar_path:
            avatar_path = 'default.png'
        else:
            avatar_path = f'users/{avatar_path}'
        friend_avatar_path.append(avatar_path)
        friend_hrefs.append('/' + friend_data.tag)
        friend_tags.append(friend_data.tag)
    friends_data = {
        'friend_names': friend_names,
        'friend_learn': friend_learn,
        'friend_avatar_path': friend_avatar_path,
        'friend_hrefs': friend_hrefs,
        'friend_tags': friend_tags
    }

    incoming_requests = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).order_by(FriendRequest.id.desc()).all()
    friend_names = []
    friend_learn = []
    friend_avatar_path = []
    friend_hrefs = []
    friend_tags = []
    incoming_requests_user_ids = [req.user_id for req in incoming_requests]
    incoming_requests_count = len(incoming_requests)
    users = User.query.filter(User.id.in_(incoming_requests_user_ids)).all()

    for user1 in users:
        friend_names.append(user1.name + " " + user1.second_name)
        if user1.show_education == '1':
            friend_learn.append(user1.education_place)
        else:
            friend_learn.append(None)
        avatar_path = user1.avatar_path
        if not avatar_path:
            avatar_path = 'default.png'
        else:
            avatar_path = f'users/{avatar_path}'
        friend_avatar_path.append(avatar_path)
        friend_hrefs.append('/' + user1.tag)
        friend_tags.append(user1.tag)

    request_all_data = {
        'friend_names': friend_names,
        'friend_learn': friend_learn,
        'friend_avatar_path': friend_avatar_path,
        'friend_hrefs': friend_hrefs,
        'friend_tags': friend_tags
    }


    outgoing_requests = FriendRequest.query.filter_by(user_id=request.cookies.get('account')).order_by(FriendRequest.id.desc()).all()
    friend_names = []
    friend_learn = []
    friend_avatar_path = []
    friend_hrefs = []
    friend_tags = []
    outgoing_requests_user_ids = [req.friend_id for req in outgoing_requests]
    outgoing_requests_count = len(outgoing_requests)
    users = User.query.filter(User.id.in_(outgoing_requests_user_ids)).all()

    for user2 in users:
        friend_names.append(user2.name + " " + user2.second_name)
        if user2.show_education == '1':
            friend_learn.append(user2.education_place)
        else:
            friend_learn.append(None)
        avatar_path = user2.avatar_path
        if not avatar_path:
            avatar_path = 'default.png'
        else:
            avatar_path = f'users/{avatar_path}'
        friend_avatar_path.append(avatar_path)
        friend_hrefs.append('/' + user2.tag)
        friend_tags.append(user2.tag)

    request_outgoing_data = {
        'friend_names': friend_names,
        'friend_learn': friend_learn,
        'friend_avatar_path': friend_avatar_path,
        'friend_hrefs': friend_hrefs,
        'friend_tags': friend_tags
    }

    notifications, notifications_count = check_notification(request.cookies.get('account'))
    return render_template('friends.html',
                           me=User.query.filter_by(id=request.cookies.get('account')).first(),
                           user=User.query.filter_by(id=request.cookies.get('account')).first(),
                           user_page = user,
                           request_all_data = request_all_data,
                           incoming_requests_count = incoming_requests_count,
                           request_outgoing_data = request_outgoing_data,
                           outgoing_requests_count = outgoing_requests_count,
                           friends_data=friends_data,
                           friends_count=friends_count,
                           _self=_self,
                           notifications=notifications,
                           notification_count=notifications_count,
                           section = section,
                           self_avatar_path = User.query.filter_by(id=request.cookies.get('account')).first().avatar_path,
                           )




@app.route('/friends/load-more', methods=['POST'])
def load_more_friends():
    offset = request.json.get('count')
    user_tag = request.json.get('user_tag')
    user = User.query.filter_by(tag=user_tag).first()

    filter = request.args.get('filter')

    try:
        if not filter:
            friends = Friends.query.filter_by(user_id=user.id).order_by(Friends.id.desc()).offset(offset).limit(15).all()
        else:
            search_string = f"%{filter}%"
            for search_string in [search_string, search_string.title()]:
                users = User.query.filter(or_(
                    User.name.like(search_string),
                    User.second_name.like(search_string),
                    text(f"({User.name} || ' ' || {User.second_name}) LIKE :search_string")
                )).params(search_string=search_string).all()
            user_ids = [user.id for user in users]

            users = User.query.filter(User.tag.like(search_string)).all()
            user_ids2 = [user.id for user in users]

            user_ids.extend(user_ids2)

            friends = Friends.query.filter_by(user_id=user.id).filter(Friends.friend_id.in_(user_ids)).all()


        friend_names = []
        friend_learn = []
        friend_avatar_path = []
        friend_hrefs = []
        friend_tags = []

        for friend in friends:
            friend_data = User.query.filter_by(id=friend.friend_id).first()
            friend_names.append(f'{friend_data.name} {friend_data.second_name}')
            if friend_data.show_education == '1':
                friend_learn.append(friend_data.education_place)
            else:
                friend_learn.append(None)
            avatar_path = friend_data.avatar_path
            if not avatar_path:
                avatar_path = 'default.png'
            else:
                avatar_path = f'users/{avatar_path}'
            friend_avatar_path.append(avatar_path)
            friend_hrefs.append('/' + friend_data.tag)
            friend_tags.append(friend_data.tag)

        friends_data = {
            'success': True,
            'names': friend_names,
            'learns': friend_learn,
            'avatar_paths': friend_avatar_path,
            'hrefs': friend_hrefs,
            'tags': friend_tags
        }
        return jsonify(friends_data)
    except Exception as e:
        return jsonify({'success': False})

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

@app.route('/comments/load', methods = ['POST'])
def loadComments():
    if request.method == 'POST':
        offset = request.json.get('offset')
        
        postId = request.json.get('postId')
        comments = Comments.query.filter_by(post_id=postId).order_by(Comments.id.desc()).offset(offset).limit(5).all()
        
        usernames = []
        avatar_paths = []
        texts = []
        times = []
        selfs = []
        hrefs = []
        ids = []
        for comment in comments:
            user = User.query.filter_by(id=comment.user_id).first()
            usernames.append(user.name + " " + user.second_name)
            if user.avatar_path:
                avatar_paths.append(user.avatar_path)
            else:
                avatar_paths.append('../default.png')
            texts.append(comment.text)
            times.append(comment.time)
            selfs.append(str(comment.user_id) == request.cookies.get('account'))
            hrefs.append(user.tag)
            ids.append(comment.id)

        post = Post.query.filter_by(id=postId).all()
        avatar = User.query.filter_by(id=request.cookies.get('account')).first().avatar_path
        selfAvatar = avatar

        data = {
            'success': True,
            'usernames': usernames,
            'avatar_paths': avatar_paths,
            'texts': texts,
            'times': times,
            'selfs': selfs,
            'hrefs': hrefs,
            'ids': ids,
            'selfAvatar': selfAvatar,
            'post_id': postId
        }


        return jsonify(data)

@app.route('/comments/delete', methods=['POST'])
def deleteComment():
    if request.method == "POST":
        commentId = request.json.get('id')

        comment = Comments.query.filter_by(id=commentId).first()
        post_id = comment.post_id
        try:
            db.session.delete(comment)
            db.session.commit()

            post = Post.query.filter_by(id=post_id).first()
            post.comments -= 1
            db.session.commit()

            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False})



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

@app.route('/edit_group', methods=["GET"])
def edit_group():
    if request.method == "GET":
        group_id = request.args.get('id')
        if Group.query.filter_by(id=group_id).first().owner_id == int(request.cookies.get('account')):
            group = Group.query.filter_by(id=group_id).first()

            if group:
                return render_template('edit_group.html', group=group)
            else:
                return 'Страница не найдена'
        else:
            return 'Нет доступа'


@app.route('/groups/tag/check-unique', methods=["POST"])
def check_unique_tag():
    if request.method == "POST":
        tag = request.json.get('tag')
        groups_with_this_tag = Group.query.filter_by(tag=tag).count()
        if groups_with_this_tag == 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})

@app.route('/groups/update', methods=["POST"])
def update_group():
    if request.method == "POST":
        tag = request.form.get('old_tag')
        group = Group.query.filter_by(tag=tag).first()
        new_tag = request.form.get('new_tag')
        name = request.form.get('name')
        if len(name) < 3:
            return jsonify({'success': False, 'error': 'Имя слишком короткое'})
        avatar = request.files.get('avatar')
        if avatar:
            avatar.save(f'static/avatars/groups/avatar-group-{group.id}.{avatar.filename.split(".")[-1]}')
            group.avatar_path = f'avatar-group-{group.id}.{avatar.filename.split(".")[-1]}'
        try:
            group.name = name

            group.tag = new_tag
            db.session.commit()
            return jsonify({'success': True, 'tag':new_tag})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})





@app.route('/post/add', methods=["POST"])
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
                            newPhoto = Photos(user_id=request.cookies.get('account'), path_name=photos_url, name=f'Фото пользователя {User.query.filter_by(id=request.cookies.get("account")).first().name}', inPost='True')
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
                    newVideo = Video(user_id=request.cookies.get('account'), path_name=video_url, name=f'Видео пользователя {User.query.filter_by(id=request.cookies.get("account")).first().name}', inPost="True")
                    db.session.add(newVideo)
                    db.session.commit()
                    return jsonify({'result': True})
                except:
                    db.session.rollback()
                    return jsonify({'result': False})


    return jsonify({'result': False})



@app.route('/community/post-add', methods=["POST"])
def addPost_group():
    if request.method == "POST":
        print(0)
        if request.json.get('type') == 'main':
            print(1)
            text = request.json.get('text')
            tag = request.json.get('tag')
            id = Group.query.filter_by(tag=tag).first().id

            photos = request.json.get('photos')
            photos_urls = []
            for photo in photos:
                print(2)
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
            print(3)
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
            new_post = Post(user_id=id, text=text, images=_photos_urls, date=date, isGroup='1')
            print(4)
            try:
                db.session.add(new_post)
                db.session.commit()
                print(5)
                return jsonify({'result': True})


            except Exception as e:
                db.session.rollback()
                print(6)
                return jsonify({'result': False})




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
                    newVideo = Video(user_id=request.cookies.get('account'), path_name=video_url, name=f'Видео пользователя {User.query.filter_by(id=request.cookies.get("account")).first().name}', inPost="True")
                    db.session.add(newVideo)
                    db.session.commit()
                    return jsonify({'result': True})
                except:
                    db.session.rollback()
                    return jsonify({'result': False})


    return jsonify({'result': False})




@app.route('/group/subscribe', methods=["POST"])
def subscribe():
    user = request.cookies.get('account')
    group_tag = request.json.get('tag')
    group = Group.query.filter_by(tag=group_tag).first()

    if not Subscribe.query.filter_by(user_id=user).filter_by(group_id=group.id).first():
        group = Group.query.filter_by(tag=group_tag).first()
        if group.subscribers is None:
            group.subscribers = 0
        group.subscribers += 1
        db.session.add(Subscribe(user_id=user, group_id=group.id))
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/group/unsubscribe', methods=["POST"])
def g_unsubscribe():
    user = request.cookies.get('account')
    group_tag = request.json.get('tag')
    group = Group.query.filter_by(tag=group_tag).first()

    subs = Subscribe.query.filter_by(user_id=user).filter_by(group_id=group.id).first()
    group = Group.query.filter_by(tag=group_tag).first()
    group.subscribers -= 1
    if subs:
        db.session.delete(subs)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/<string:tag>', methods=['GET'])
@check_access
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

        incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()
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

        posts = Post.query.filter_by(isGroup=None).filter_by(user_id=request.cookies.get('account')).order_by(Post.id.desc()).limit(5).all()
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

        subscriptions_count = User.query.filter_by(tag=tag).first().subscriptions_count
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
                               hrefs = hrefs,
                               incoming_requests_count=incoming_requests_count,
                               subscriptions_count = subscriptions_count
        )


@app.route('/community/<string:tag>')
@check_access
def group_profile(tag):
    group = Group.query.filter_by(tag=tag).first()
    print(group)
    user = User.query.filter_by(id=request.cookies.get('account')).first()

    notifications, notifications_count = check_notification(request.cookies.get('account'))
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()


    me = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user.avatar_path


    owner = (group.owner_id == user.id)

    if Subscribe.query.filter_by(user_id=request.cookies.get('account')).filter_by(group_id=group.id).first():
        isSubscribe = 1
    else:
        isSubscribe = 0

    posts = Post.query.filter_by(isGroup='1').filter_by(user_id=group.id).order_by(Post.id.desc()).limit(5).all()
    avatars = []
    authors = []
    _selfs = []
    hrefs = []
    liked = []
    posts_files = []
    for post in posts:
        if Group.query.filter_by(id=post.user_id).first().avatar_path:
            avatars.append(f'groups/{User.query.filter_by(id=post.user_id).first().avatar_path}')
        else:
            avatars.append(f'default.png')

        username = Group.query.filter_by(id=post.user_id).first().name
        authors.append(username)

        if group.owner_id == int(request.cookies.get('account')):
            _selfs.append(1)
        else:
            _selfs.append(0)
        post_files = []

        if post.images:
            post_images = post.images.split('/')
            for file in post_images:
                post_files.append(f'groups/photos/{file}')

        if post.videos:
            post_videos = post.videos.split('/')
            for file in post_videos:
                post_files.append(f'groups/video/{file}')

        posts_files.append(post_files)

        liked_1 = Likes.query.filter_by(user_id=request.cookies.get('account'), post_id=post.id).first()

        if liked_1:
            liked.append(1)
        else:
            liked.append(0)

        hrefs.append(user.tag)

    subscriptions_count = Group.query.filter_by(tag=tag).first().subscribers
    return render_template('groupe.html',
                           user=user,
                           _selfs=_selfs,
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path=self_avatar_path,
                           me=me,
                           posts=posts,
                           avatars=avatars,
                           authors=authors,
                           posts_files=posts_files,
                           liked=liked,
                           hrefs = hrefs,
                           incoming_requests_count=incoming_requests_count,
                           subscriptions_count = subscriptions_count,
                           group = group,
                           owner=owner,
                           isSubscribe=isSubscribe
    )



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/post/like', methods=['POST'])
def likePost():
    if request.method == 'POST':
        post_id = request.json.get('id')

        like = Likes.query.filter_by(post_id=post_id, user_id=request.cookies.get('account')).first()
        post = Post.query.filter_by(id=post_id).first()
        if like:
            post.likes = post.likes - 1
            try:
                db.session.delete(like)
                db.session.commit()

                return jsonify({'success': True, 'liked': False})
            except:
                db.session.rollback()
        else:
            new_like = Likes(post_id=post_id, user_id=request.cookies.get('account'))
            post.likes = post.likes + 1
            try:
                db.session.add(new_like)
                db.session.commit()
                return jsonify({'success': True, 'liked': True})
            except:
                db.session.rollback()
    else:
        return 'Страница не найдена'

@app.route('/posts/load-more', methods=['POST'])
def loadMorePosts():
    if request.method == 'POST':
        
        startWith = request.json.get('startWith')
        all = request.json.get('all')
        count = request.json.get('count')
        if all:
            section = request.args.get('section')
            if section == 'null':
                section = 'new'

            if section == 'new':
                posts = Post.query.order_by(Post.id.desc()).offset(
                startWith).limit(count).all()
            elif section == 'popular':
                posts = Post.query.order_by(Post.likes.desc()).offset(
                startWith).limit(count).all()
                
            elif section == 'friends':
                friends = Friends.query.filter_by(user_id=request.cookies.get('account')).all()
                friends_ids = [i.friend_id for i in friends]
                posts = Post.query.filter(Post.isGroup == None).filter(Post.user_id.in_(friends_ids)).order_by(
                    Post.id.desc()).offset(startWith).limit(count).all()
            elif section == 'people':
                posts = Post.query.filter(Post.isGroup == None).order_by(Post.id.desc()).offset(startWith).limit(count).all()
            elif section == 'community':
                posts = Post.query.filter(Post.isGroup == '1').order_by(Post.id.desc()).offset(startWith).limit(count).all()
            elif section == 'subscribers':

                subscribe = [subscribe.group_id for subscribe in Subscribe.query.filter_by(user_id=request.cookies.get('account')).all()]
                posts = Post.query.filter(Post.user_id.in_(subscribe)).filter(Post.isGroup == '1').order_by(Post.id.desc()).offset(startWith).limit(
                    count).all()
        else:
            user_id = User.query.filter_by(tag=request.json.get('tag')).first().id
            posts = Post.query.filter_by(user_id=user_id).filter_by(isGroup=None).order_by(Post.id.desc()).offset(startWith).limit(count).all()


        usernames = []
        avatars = []
        selfs = []
        tags = []
        texts = []
        files = []
        dates = []
        ids = []
        liked = []
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
                usernames.append(f"{User.query.filter_by(id=post.user_id).first().name} {User.query.filter_by(id=post.user_id).first().second_name}")
                if post.user_id == int(request.cookies.get('account')):
                    selfs.append(1)
                else:
                    selfs.append(0)
                tags.append(User.query.filter_by(id=post.user_id).first().tag)
                if User.query.filter_by(id=post.user_id).first().avatar_path:
                    avatars.append('users/' + User.query.filter_by(id=post.user_id).first().avatar_path)
                else:
                    avatars.append('default.png')

            like = Likes.query.filter_by(post_id=post.id, user_id=request.cookies.get('account')).first()
            if like:
                liked.append(1)
            else:
                liked.append(0)

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
            'ids': ids,
            'liked': liked
        }

        if posts:
            return jsonify(posts_json)
        else:
            return jsonify({'success': False})
    return 'Страница не найдена'

@app.route('/post/remove', methods=['POST'])
def removePost():
    if request.method == 'POST':
        post_id = int(request.json.get('id'))

        try:
            post = Post.query.filter_by(id=post_id).first()

            if post:
                likes = Likes.query.filter_by(post_id=post_id).all()
                for like in likes:
                    db.session.delete(like)
                db.session.delete(post)
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


@app.route('/notification/view', methods=["POST"])
def notificationView():
    if request.method == "POST":
        id = request.cookies.get('account')
        notifications = Notification.query.filter_by(user_id=id, new=1).all()
        for notification in notifications:
            notification.new = 0
            db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})



@app.route('/notification/delete', methods=["POST"])
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
                        if i.startswith(f"avatar-user-{user_id}"):
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
def add_friend_requests(data):
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

@app.route('/friend/remove', methods=['POST'])
def add_friend():
    user_id = request.cookies.get('account')
    friend_id = request.json.get('friend_id')
    if not friend_id:
        friend_tag = request.json.get('friend_tag')
        friend_id = User.query.filter_by(tag=friend_tag).first().id
    try:
        friend1 = Friends.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
        friend2 = Friends.query.filter_by(user_id=friend_id).filter_by(friend_id=user_id).first()

        db.session.delete(friend1)
        db.session.delete(friend2)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


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

@app.route('/friend/request/remove', methods=['POST'])
def rem_friend_request():
    user_tag = request.json.get('user_tag')

    if user_tag:
        friend_id = request.cookies.get('account')
        user_id = User.query.filter_by(tag=user_tag).first().id
        isCancel = False
    else:
        user_id = request.cookies.get('account')
        friend_tag = request.json.get('friend_tag')
        friend_id = User.query.filter_by(tag=friend_tag).first().id
        isCancel = True

    request1 = FriendRequest.query.filter_by(user_id=user_id).filter_by(friend_id=friend_id).first()
    try:
        db.session.delete(request1)
        db.session.commit()
        if isCancel:
            try:
                from_user = User.query.filter_by(id=user_id).first().name + " " + User.query.filter_by(
                    id=user_id).first().second_name
                notif_to_rem = Notification.query.filter_by(user_id=friend_id, from_user=from_user).filter_by(
                    type='newFriendRequest').all()
                for notif in notif_to_rem:
                    db.session.delete(notif)
                    db.session.commit()
            except:
                db.session.rollback()

        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False})

@app.route('/friend/add', methods=["POST"])
def add_friend_fetch():
    friend_id = request.cookies.get('account')
    user_tag = request.json.get('user_tag')
    user_id = User.query.filter_by(tag=user_tag).first().id


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

            try:
                notif_to_rem = Notification.query.filter_by(user_id=friend_id).filter_by(type='newFriendRequest').all()
                for notif in notif_to_rem:
                    db.session.delete(notif)
                    db.session.commit()
            except:
                db.session.rollback()

            user_name = User.query.filter_by(id=friend_id).first().name + " " + User.query.filter_by(id=friend_id).first().second_name
            from_avatar = User.query.filter_by(id=friend_id).first().avatar_path

            createNotification(user_id=user_id, type='friendRequestApprove', from_user_avatar_path=from_avatar,
                               text=f'принял Ваше предложение дружбы',
                               from_user=user_name, href=f'/{User.query.filter_by(id=friend_id).first().tag}', date=datetime.datetime.now(), room=str(user_id))


            return jsonify({'success': True})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False})



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
            from_user = User.query.filter_by(id=user_id).first().name + " " + User.query.filter_by(id=user_id).first().second_name
            print(from_user)
            notif_to_rem = Notification.query.filter_by(user_id=friend_id, from_user=from_user).filter_by(type='newFriendRequest').all()
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
            if photo.inPost == 'False':
                os.remove(f'static/users/photos/{photo.path_name}')
            socketio.emit('deletePhoto_result', {'success': True}, room=request.cookies.get('account'))

        except Exception as e:
            db.session.rollback()
            socketio.emit('deletePhoto_result', {'success': False, 'error': str(e)}, room=request.cookies.get('account'))
    else:
        socketio.emit('deletePhoto_result', {'success': False, 'error': ' Фото не найдено, обратитесь в поддержку'}, room=request.cookies.get('account'))



@app.route('/video/delete', methods=['POST'])
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
        if video.inPost == 'False':
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
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
