import base64
import logging
import os
import pprint
import threading
from functools import wraps
import secrets

import flask_mail
from flask import Flask, session, redirect, render_template, request, jsonify, make_response, send_from_directory
from flask.json import tag
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from flask_mail import Mail, Message
from sqlalchemy import func, and_, or_, text
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Friends, FriendRequest, Notification, Photos, Video, Group, Post, Likes, Comments, \
    Subscribe, Setting, TechnicalSupportRequest, Chats, Message
from config import app, action_access, month_data
import random
import datetime
import imghdr
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

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
        user = User.query.filter_by(id=session.get('account')).first()
        if not user:
            emails = [user.email for user in User.query.all()]
            return render_template('auth.html', emails=emails)
        elif not user.name:
            return redirect('/edit_user')

        return f(*args, **kwargs)

    return decorated_function

@app.route('/message/new', methods=['POST'])
def message_new():
    chat = request.json.get('chat')
    message = request.json.get('message')
    date = datetime.datetime.utcnow().strftime('%d.%m в %H:%M')
    from_user = User.query.filter_by(id=request.cookies.get('account')).first()
    to_user = User.query.filter_by(tag=chat).first()

    message1 = Message(from_user=from_user.id, to_user=to_user.id, text=message, time=date)
    try:
        db.session.add(message1)
        db.session.commit()

        socketio.emit('newMessage',{
            'success': True,
            'avatar': from_user.avatar_path,
            'name': f'{from_user.name} {from_user.second_name}',
            'message': message,
            'time': date,
            'self': False
        }, room=str(to_user.id))

        if Setting.query.filter_by(user_id=to_user.id).first().notification_message != 0:
            text = 'отправил вам сообщение'
            createNotification(user_id=to_user.id,
                               type='newMessage',
                               from_user_avatar_path=from_user.avatar_path,
                               text=text,
                               from_user=f'{from_user.name}',
                               href=from_user.tag,
                               date=datetime.datetime.now(),
                               room=str(to_user.id)
                               )

        chats = Chats.query.filter(
            or_(
                and_(
                    Chats.user_id==from_user.id,
                    Chats.user2_id==to_user.id
                ),
                and_(
                    Chats.user_id==to_user.id,
                    Chats.user2_id==from_user.id
                )
            )
        ).all()
        if len(chats) == 1:
            new_chat = Chats(user_id=to_user.id, user2_id=from_user.id)
            try:
                db.session.add(new_chat)
                db.session.commit()
                chats.append(new_chat)
            except:
                db.session.rollback()
        for chat in chats:
            chat.last_message = message
            chat.last_message_time = datetime.datetime.now()
            try:
                db.session.commit()
            except:
                db.session.rollback()

        return jsonify({
            'success': True,
            'avatar': from_user.avatar_path,
            'name': f'{from_user.name} {from_user.second_name}',
            'message': message,
            'time': date,
            'self': False
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/messanger/remove/<int:chat_id>', methods=['POST'])
def remove_chat(chat_id):
    chat = Chats.query.filter_by(id=chat_id).first()
    if chat.user_id == int(request.cookies.get('account')):
        try:
            db.session.delete(chat)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify({'success': False, 'error': 'Внедрение в код запрещено!'})


@app.route('/messanger')
def messanger():
    chat = request.args.get('chat')
    notifications, notifications_count = check_notification(request.cookies.get('account'))

    user_self = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user_self.avatar_path
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()

    self_id = request.cookies.get('account')

    if chat:
        interlocutor = User.query.filter_by(tag=chat).first()
        messages = Message.query.filter(or_(
            and_(
                Message.from_user==self_id,
                Message.to_user==interlocutor.id
            ),
            and_(
                Message.from_user == interlocutor.id,
                Message.to_user == self_id
            )
        )).limit(500).all()

        avatars = []
        names = []
        tags = []
        for message in messages:
            user = User.query.filter_by(id=message.from_user).first()
            if user.avatar_path:
                avatars.append(user.avatar_path)
            else:
                avatars.append(None)
            names.append(user.name + ' ' + user.second_name)
            tags.append(user.tag)

        if not Chats.query.filter_by(user_id=request.cookies.get('account')).filter(Chats.user2_id==interlocutor.id).first():
            chat = Chats(user_id=request.cookies.get('account'), user2_id=interlocutor.id)
            try:
                db.session.add(chat)
                db.session.commit()
            except:
                db.session.rollback()

        return render_template('chat.html',
                               messages=messages,
                               notifications=notifications,
                               notification_count=notifications_count,
                               user=user_self,
                               self_avatar_path=self_avatar_path,
                               me=me,
                               incoming_requests_count=incoming_requests_count,
                               interlocutor=interlocutor,
                               avatars=avatars,
                               names=names,
                               tags=tags)

    else:
        filter = request.args.get('filter')
        if filter:
            search_string = f"%{filter}%"
            for search_string in [search_string, search_string.title()]:
                users = User.query.filter(or_(
                    User.name.like(search_string),
                    User.second_name.like(search_string),
                    text(f"({User.name} || ' ' || {User.second_name}) LIKE :search_string"),
                    User.tag.like(search_string)
                )).params(search_string=search_string).limit(20).all()
            users_ids = [user.id for user in users]

            chats = Chats.query.filter_by(user_id=request.cookies.get('account')).filter(Chats.user2_id.in_(users_ids)).order_by(Chats.id.desc()).all()
        else:
            chats = Chats.query.filter_by(user_id=request.cookies.get('account')).order_by(Chats.id.desc()).all()
        users = []

        last_messages = []
        for user_chat in chats:
            user = User.query.filter_by(id=user_chat.user2_id).first()
            users.append(user)
            last_message = Message.query.filter_by(from_user=user.id, to_user=self_id).order_by(Message.id.desc()).all()
            last_messages.append(last_message)
        chat_count = len(chats)

        return render_template('chats.html',
                               chats=chats,
                               users=users,
                               chat_count=chat_count,
                               user=user_self,
                               me=me,
                               self_avatar_path=self_avatar_path,
                               notifications=notifications,
                               incoming_requests_count=incoming_requests_count,
                               notification_count=notifications_count,
                               filter=filter)
@app.route('/notification/send', methods=['POST'])
def send_notification():
    text = request.json.get('text')
    tag = request.json.get('tag')

    user = User.query.filter_by(tag=tag).first()
    try:
        support_tag = User.query.filter_by(id=request.cookies.get('account')).first().tag
        createNotification(user.id, 'SupportMessage', 'support.png', text, '/messanger?chat=' + support_tag, datetime.datetime.now(), support_tag, str(user.id))

        msg = flask_mail.Message('Обернет. Ответ техподдержки',
                      recipients=[user.email])
        msg.body = 'Получен ответ он техподдержки. Он также продублирован в уведомлениях на сайте'
        msg.html = f'{text} <br> Ссылку на переписку с поддержкой смотрите в уведомлениях сайта. '

        with app.app_context():
            mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/support/request/remove', methods=['POST'])
def remove_request():
    req_id = request.json.get('id')

    request1 = TechnicalSupportRequest.query.filter_by(id=req_id).first()
    try:
        db.session.delete(request1)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/support')
# @check_status('support')
def admin_support():
    filter = request.args.get('q')
    if not filter:
        filter = 'all'

    users = []
    if filter == 'all':
        support_requests = TechnicalSupportRequest.query.filter_by(status='Открыт').order_by(
            TechnicalSupportRequest.id).all()
        for i in support_requests:
            users.append(User.query.filter_by(id=i.user_id).first().tag)
    else:
        support_requests = TechnicalSupportRequest.query.filter_by(status='Открыт', theme=filter).order_by(
            TechnicalSupportRequest.id).all()
        for i in support_requests:
            users.append(User.query.filter_by(id=i.user_id).first().tag)

    count = len(support_requests)
    return render_template('admin_support.html',
                           support_requests=support_requests,
                           count=count,
                           users=users,
                           filter=filter)



@app.route('/admin/change_status')
@check_status('change_status')
def change_status():
    return render_template('change_status.html')

@app.route('/comments/add', methods=['POST'])
@app.route('/community/comments/add', methods=['POST'])
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


@app.route('/photos')
def photos():
    notifications, notifications_count = check_notification(request.cookies.get('account'))
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user.avatar_path
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()


    user_tag = request.args.get('user')
    user_photo = User.query.filter_by(tag=user_tag).first()
    photos = Photos.query.filter_by(user_id=user_photo.id).all()

    _self = (user_tag == user.tag)
    return render_template('images.html',
                           photos=photos,
                           _self = _self,
                           user=user,
                           me=me,
                           incoming_requests_count=incoming_requests_count,
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path=self_avatar_path
                           )

@app.route('/video')
def videos():
    notifications, notifications_count = check_notification(request.cookies.get('account'))
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user.avatar_path
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()


    user_tag = request.args.get('user')
    user_video = User.query.filter_by(tag=user_tag).first()
    videos = Video.query.filter_by(user_id=user_video.id).all()

    _self = (user_tag == user.tag)
    return render_template('video.html',
                           videos=videos,
                           _self = _self,
                           user=user,
                           me=me,
                           incoming_requests_count=incoming_requests_count,
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path=self_avatar_path
                           )

@app.route('/setting/notification/update', methods=['POST'])
def update_notification():
    type = request.json.get('type')
    value = request.json.get('val')

    setting = Setting.query.filter_by(user_id=request.cookies.get('account')).first()
    if not setting:
        setting = Setting(user_id=request.cookies.get('account'))
        db.session.add(setting)
        db.session.commit()

    if type == 'friend-request':
        setting.notification_friend_request = value
    elif type == 'friend-status':
        setting.notification_friend_access = value
    elif type == 'message':
        setting.notification_message = value
    elif type == 'friend-post':
        setting.notification_friend_posts = value
    elif type == 'community-post':
        setting.notification_community_posts = value
    else:
        return jsonify({'success': False})

    try:
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False})


@app.route('/setting/privacy/update', methods=['POST'])
def update_privacy():
    type = request.json.get('type')
    value = request.json.get('val')

    setting = Setting.query.filter_by(user_id=request.cookies.get('account')).first()
    user = User.query.filter_by(id=request.cookies.get('account')).first()

    if not setting:
        setting = Setting(user_id=request.cookies.get('account'))
        db.session.add(setting)
        db.session.commit()

    if type == 'profile_open':
        setting.profile_open = value
    elif type == 'friend-show_date_of_birthday':
        user.show_date_of_birthday = str(value)
    elif type == 'show_gender':
        user.show_gender = str(value)
    elif type == 'show_education':
        user.show_education = str(value)
    elif type == 'show_city':
        user.show_city = str(value)
    else:
        return jsonify({'success': False})

    try:
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'success': False})

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



@app.route('/setting')
def setting():
    notifications, notifications_count = check_notification(request.cookies.get('account'))
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user.avatar_path
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()
    section = request.args.get('q')
    if not section:
        section = 'general'

    setting = Setting.query.filter_by(user_id=request.cookies.get('account')).first()


    return render_template('setting.html',
                           user=user,
                           me=me,
                           incoming_requests_count=incoming_requests_count,
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path = self_avatar_path,
                           section=section,
                           setting=setting
                           )


@app.route('/profile/remove', methods=['POST'])
def remove_profile():
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    try:
        subscribers = Subscribe.query.filter_by(user_id=user.id).all()
        for subscriber in subscribers:
            db.session.delete(subscriber)
    except:
        pass
    try:
        friends = Friends.query.filter_by(user_id=user.id).all()
        for friend in friends:
            db.session.delete(friend)
    except:
        pass
    try:
        friend_requests = FriendRequest.query.filter_by(user_id=user.id).all()
        for friend_request in friend_requests:
            db.session.delete(friend_request)
    except:
        pass
    try:
        notifications = Notification.query.filter_by(user_id=user.id).all()
        for notification in notifications:
            db.session.delete(notification)
    except:
        pass
    try:
        photos = Photos.query.filter_by(user_id=user.id).all()
        for photo in photos:
            db.session.delete(photo)
    except:
        pass
    try:
        videos = Video.query.filter_by(user_id=user.id).all()
        for video in videos:
            db.session.delete(video)
    except:
        pass
    try:
        posts = Post.query.filter_by(user_id=user.id).all()
        for post in posts:
            db.session.delete(post)
    except:
        pass
    try:
        likes = Likes.query.filter_by(user_id=user.id).all()
        for like in likes:
            db.session.delete(like)
    except:
        pass
    try:
        comments = Comments.query.filter_by(user_id=user.id).all()
        for comment in comments:
            db.session.delete(comment)
    except:
        pass
    try:
        settings = Setting.query.filter_by(user_id=request.cookies.get('account')).first()
        db.session.delete(settings)
    except:
        pass

    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})




@app.route('/privacy')
def in_dev():
    return render_template('in-dev.html')

@app.route('/support', methods=['GET'])
def support():
    notifications, notifications_count = check_notification(request.cookies.get('account'))
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user.avatar_path
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()

    return render_template('support.html',
                           user=user,
                           me=me,
                           self_avatar_path=self_avatar_path,
                           notifications=notifications,
                           notification_count=notifications_count,
                           incoming_requests_count=incoming_requests_count
                           )

@app.route('/support/request/add', methods=['POST'])
def add_request():
    theme = request.json.get('theme')
    info = request.json.get('info')
    phone = request.json.get('phone')
    user = User.query.filter_by(id=request.cookies.get('account')).first()

    try:
        newRequest = TechnicalSupportRequest(user_id=user.id, theme=theme, info=info, user_phone=phone)
        db.session.add(newRequest)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/groups')
@check_access
def groops():
    section = request.args.get('section')
    if not section:
        section = 'all'

    self_group = Group.query.filter_by(owner_id=request.cookies.get('account')).all()
    self_group_count = len(self_group)

    user_tag = request.args.get('user')
    user = User.query.filter_by(tag=user_tag).first()

    groops_subs = Subscribe.query.filter_by(user_id=user.id).limit(15).all()
    groops_data_count = Subscribe.query.filter_by(user_id=user.id).count()

    groops_ids = [i.group_id for i in groops_subs]
    groops_ids.extend(i.id for i in self_group)
    if section == 'all':
        # groops = Group.query.filter(Group.id.in_(groops_ids)).all()
        groops = []
        for id in groops_ids:
            groops.append(Group.query.filter_by(id=id).first())
    elif section == 'owner':
        groops = self_group


    titles = []
    hrefs = []
    tags = []
    avatar_paths = []
    subscribers = []
    owner = []

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

        if group.owner_id == int(request.cookies.get('account')):
            own = 1
        else:
            own = 0
        owner.append(own)

    groops_data = {
        'titles': titles,
        'hrefs': hrefs,
        'tags': tags,
        'avatar_paths': avatar_paths,
        'subscribers': subscribers,
        'owners': owner
    }

    _self = (str(user.id) == request.cookies.get('account'))

    notifications, notifications_count = check_notification(request.cookies.get('account'))

    incoming_requests = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).order_by(
        FriendRequest.id.desc()).all()

    profile_open = Setting.query.filter_by(user_id=user.id).first().profile_open
    if profile_open == 0:
        isFriend1 = Friends.query.filter_by(user_id=request.cookies.get('account')).filter_by(friend_id=user.id).first()
        if isFriend1:
            profile_open = 1
        if user.id == int(request.cookies.get('account')):
            profile_open = 1
    return render_template('user-groups.html',
                           groops_data=groops_data,
                           _self=_self,
                           user_page=user,
                           groops_data_count=groops_data_count,
                           me=User.query.filter_by(id=request.cookies.get('account')).first(),
                           user=User.query.filter_by(id=request.cookies.get('account')).first(),
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path = User.query.filter_by(id=request.cookies.get('account')).first().avatar_path,
                           incoming_requests_count=len(incoming_requests),
                           section=section,
                           self_group_count=self_group_count,
                           profile_open=profile_open,
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
            for search_string in [search_string, search_string.title()]:
                groups = Group.query.filter(Group.name.like(search_string)).all()
            group_ids = [group.id for group in groups]

            groups = User.query.filter(User.tag.like(search_string)).all()
            groups_ids2 = [group.id for group in groups]

            group_ids.extend(groups_ids2)

            subscribers = Subscribe.query.filter_by(user_id=user.id).filter(Subscribe.group_id.in_(group_ids)).limit(50).all()

        names = []
        subs = []
        avatar_paths = []
        hrefs = []
        tags = []
        owners = []

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
                avatar_path = f'groups/{avatar_path}'
            avatar_paths.append(avatar_path)
            hrefs.append('/community/' + friend_data.tag)
            tags.append(friend_data.tag)

            if friend_data.owner_id == request.cookies.get('account'):
                own = 1
            else:
                own = 0
            owners.append(own)
        _self = (str(User.query.filter_by(tag=user_tag).first().id) == request.cookies.get('account'))
        friends_data = {
            'success': True,
            'title': names,
            'subs': subs,
            'avatar_paths': avatar_paths,
            'hrefs': hrefs,
            'tags': tags,
            'self': _self,
            'owners': owners
        }
        return jsonify(friends_data)
    except Exception as e:
        return jsonify({'success': False})


@app.route('/search', methods=['GET'])
def search_get():
    return redirect('/search/people')

@app.route('/search/<string:content>')
@check_access
def search(content):
    filter = request.args.get('q')
    if not filter:
        filter = ''
    result = []
    search_string = f"%{filter}%"
    if content == 'people':
        for search_string in [search_string, search_string.title()]:
            users = User.query.filter(or_(
                User.name.like(search_string),
                User.second_name.like(search_string),
                text(f"({User.name} || ' ' || {User.second_name}) LIKE :search_string"),
                User.tag.like(search_string)
            )).params(search_string=search_string).limit(20).all()

        result.extend(users)


    elif content == 'community':
        groups = Group.query.filter(or_(
            Group.name.like(search_string),
            Group.tag.like(search_string))).all()

        result.extend(groups)


    else:
        return redirect('/search')

    if filter == '':
        result = []

    notifications, notifications_count = check_notification(request.cookies.get('account'))
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    self_avatar_path = user.avatar_path
    me = User.query.filter_by(id=request.cookies.get('account')).first()
    incoming_requests_count = FriendRequest.query.filter_by(friend_id=request.cookies.get('account')).count()
    return render_template('search.html',
                           content=content,
                           filter=filter,
                           user=user,
                           me=me,
                           incoming_requests_count=incoming_requests_count,
                           notifications=notifications,
                           notification_count=notifications_count,
                           self_avatar_path = self_avatar_path,
                           result=result,
                           result_count = len(result)
                           )


@app.route('/search/people/load-more', methods=['POST'])
def serch_loadMore_users():
    offset = request.json.get('count')
    filter = request.json.get('filter')

    search_string = f"%{filter}%"

    users = []
    for search_string in [search_string, search_string.title()]:
        user = User.query.filter(or_(
            User.name.like(search_string),
            User.second_name.like(search_string),
            text(f"({User.name} || ' ' || {User.second_name}) LIKE :search_string"),
            User.tag.like(search_string)
        )).params(search_string=search_string).offset(offset).limit(20).all()
        users.extend(user)

    avatars = []
    names = []
    cities = []
    hrefs = []

    for user in users:
        avatar_path = f'users/{user.avatar_path}'
        if not avatar_path:
            avatar_path = 'default.png'
        name = user.name + " " + user.second_name
        if user.show_city == 1:
            place = user.country + ", " + user.city
        else:
            place = None
        href = f'/{user.tag}'

        avatars.append(avatar_path)
        names.append(name)
        cities.append(place)
        hrefs.append(href)

    data = {
        'success': True,
        'avatars': avatars,
        'names': names,
        'cities': cities,
        'hrefs': hrefs,
    }

    return jsonify(data)


@app.route('/search/community/load-more', methods=['POST'])
def serch_loadMore_groups():
    offset = request.json.get('count')
    filter = request.json.get('filter')

    search_string = f"%{filter}%"

    groups = Group.query.filter(or_(
        Group.name.like(search_string),
        Group.tag.like(search_string))).all()



    avatars = []
    names = []
    subscribers = []
    hrefs = []

    for group in groups:
        avatar_path = f'groups/{group.avatar_path}'
        if not avatar_path:
            avatar_path = 'default.png'
        name = group.name
        if group.subscribers:
            subscribers.append(group.subscribers)
        else:
            subscribers.append(0)
        href = f'/{group.tag}'

        avatars.append(avatar_path)
        names.append(name)
        hrefs.append(href)

    data = {
        'success': True,
        'avatars': avatars,
        'names': names,
        'subscribers': subscribers,
        'hrefs': hrefs,
    }

    return jsonify(data)

@app.route('/groups/delete', methods=['POST'])
def delete():
    group_tag = request.json.get('tag')
    group = Group.query.filter_by(tag=group_tag).first()

    if group:
        if group.owner_id == int(request.cookies.get('account')):
            posts = Post.query.filter_by(isGroup='1').filter_by(user_id=group.id).all()
            for post in posts:
                db.session.delete(post)
            db.session.delete(group)
            db.session.commit()
            return jsonify({'success': True})
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
        print(friend_data)
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

    profile_open = Setting.query.filter_by(user_id=user.id).first().profile_open
    if profile_open == 0:
        isFriend1 = Friends.query.filter_by(user_id=request.cookies.get('account')).filter_by(friend_id=user.id).first()
        if isFriend1:
            profile_open = 1
        if user.id == int(request.cookies.get('account')):
            profile_open = 1

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
                           profile_open=profile_open,
                           )


@app.route('/reset-password/update-password', methods=['POST'])
def update_password():
    token = request.json.get('hash')
    password = request.json.get('password')
    id = r.get(f'user-hash-{token}').decode('utf-8')
    redis_token = r.get(f'user-{id}-resetPasswordToken').decode('utf-8')
    if redis_token == token:
        user = User.query.filter_by(id=id).first()
        user.password = generate_password_hash(password)
        db.session.commit()

        createNotification(user_id=user.id, type='login-to-account', from_user_avatar_path='warn.png',
                           text=f'Изменен пароль от аккаунта {user.tag} через браузер {request.headers.get("User-Agent")}. Если это были не Вы - смените пароль в ',
                           from_user='настройках', href='/setting', date=datetime.datetime.now(), room=str(user.id))

        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Ошибка'})
@app.route('/reset-password', methods=['GET'])
def reset_password():
    tab = request.args.get('tab')
    if tab == 'input-email':
        return render_template('reset-password/input-email.html')
    elif tab == 'enter-code':
        return render_template('reset-password/input-code.html')
    elif tab == 'input-newPassword':
        return render_template('reset-password/reset-password.html')
    else:
        return 'Страница не найдена'


@app.route('/reset-password/check-code', methods=['POST'])
def check_code():
    print(1)
    code = request.json.get('code')
    token = request.json.get('session')

    id = r.get(f'user-hash-{token}').decode('utf-8')
    redis_token = r.get(f'user-{id}-resetPasswordToken').decode('utf-8')

    if redis_token == token:
        redis_code = r.get(f'user-{id}-recovery-code').decode('utf-8')
        if redis_code == code:
            return jsonify({'success': True, 'session': token})
    return jsonify({'success': False})

@app.route('/reset-password/check-data', methods=['POST'])
def reset_password_check_data():
    email = request.json['email']
    name = request.json['name']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'Пользователь не найден'})
    if user.name.lower() != name.lower():
        return jsonify({'success': False, 'error': 'Имя введено не верно'})

    code = random.randint(100000, 999999)
    token = secrets.token_hex(16)

    r.set(f'user-{user.id}-recovery-code', str(code), ex=180)
    r.set(f'user-{user.id}-resetPasswordToken', str(token), ex=180)
    r.set(f'user-hash-{token}', str(user.id), ex=180)

    msg = flask_mail.Message(subject='Код подтверждения', recipients=[email])


    with open('templates/send.html', 'r', encoding='utf-8') as f:
        text = f.read()
        textSplit = text.split('//////')
        textSplit.append(textSplit[1])
        textSplit[1] = str(code)
        result = ''.join(textSplit)
    msg.html = result
    mail.send(msg)

    print(r.get(f'user-{user.id}-resetPasswordToken'))
    return jsonify({'success': True, 'token': token})

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

def delete_secret_key():
    with app.app_context():
        if 'secret_key' in session:
            del session['secret_key']

@app.route('/check-password', methods=['POST'])
def check_password():
    password = request.json.get('password')
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    if user:
        if check_password_hash(user.password, password):
            secret_key = secrets.token_hex(16)
            session['secret_key'] = secret_key
            timer = threading.Timer(300, delete_secret_key)
            timer.start()
            return jsonify({'success': True, 'secret_key': secret_key})

    return jsonify({'success': False})

@app.route('/new-password', methods=['POST'])
def new_password():
    user = User.query.filter_by(id=request.cookies.get('account')).first()
    password = request.json.get('password')
    secret_key = request.json.get('secret_key')

    if 'secret_key' in session:
        if secret_key == session.get('secret_key'):
            del session['secret_key']
            user.password = generate_password_hash(password)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False, 'error': 'code_injection'})



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
@app.route('/community/comments/load', methods = ['POST'])
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
@app.route('/community/comments/delete', methods=['POST'])
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
        msg = flask_mail.Message(subject='Код подтверждения', recipients=[email])
        
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

                settings = Setting(user_id=user.id)
                db.session.add(settings)
                db.session.commit()
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

            friends = Friends.query.filter_by(friend_id=request.cookies.get('account')).all()
            friends_ids = [friend.user_id for friend in friends]
            users = User.query.filter(User.id.in_(friends_ids)).all()
            self_user = User.query.filter_by(id=request.cookies.get("account")).first()

            for user in users:
                setting = Setting.query.filter_by(user_id=user.id).first()
                if setting:
                    if setting.notification_friend_posts != 0:
                        text = 'добавил новую запись на странице'
                        if self_user.gender == 'woman':
                            text = 'добавила новую запись на странице'

                        createNotification(user_id=user.id, type='newUserPost', from_user_avatar_path=self_user.avatar_path,
                                           text=text,
                                           from_user=f'{self_user.name} {self_user.second_name}',
                                           href=f'/{self_user.tag}',
                                           date=datetime.datetime.now(),
                                           room=str(user.id)
                                           )


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



@app.route('/community/post/add', methods=["POST"])
def addPostGroup():
    if request.method == "POST":
        if request.json.get('type') == 'main':
            text = request.json.get('text')
            tag = request.json.get('tag')

            group = Group.query.filter_by(tag=tag).first()
            id = group.id

            photos = request.json.get('photos')
            photos_urls = []
            for photo in photos:
                base64_str = photo.split(';base64,')[-1]
                image_binary = base64.b64decode(base64_str)
                photos_url = f'{request.cookies.get("account")} - {secrets.token_hex(16)}.png'
                try:
                    with open(f'static/groups/photo/{photos_url}', 'wb') as f:
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
            new_post = Post(user_id=id, text=text, images=_photos_urls, date=date, isGroup='1')
            try:
                db.session.add(new_post)
                db.session.commit()

                friends = Friends.query.filter_by(friend_id=request.cookies.get('account')).all()
                subscribers = Subscribe.query.filter_by(group_id=group.id)
                subscribers_ids = [subscriber.user_id for subscriber in subscribers]
                users = User.query.filter(User.id.in_(subscribers_ids)).all()

                for user in users:
                   if Setting.query.filter_by(user_id=user.id).first().notification_community_posts != 0:
                    text = 'добавило новую запись на стене'

                    createNotification(user_id=user.id,
                                       type='newGroupPost',
                                       from_user_avatar_path=group.avatar_path,
                                       text=text,
                                       from_user=f'{group.name}',
                                       href=f'/community/{group.tag}',
                                       date=datetime.datetime.now(),
                                       room=str(user.id)
                                       )

                return jsonify({'result': True})


            except Exception as e:
                db.session.rollback()
                return jsonify({'result': False})




        elif request.json.get('type') == 'video':
            tag = request.json.get('tag')
            id = Group.query.filter_by(tag=tag).first().id
            video = request.json.get('data')
            base64_str = video.split(';base64,')[-1]
            image_binary = base64.b64decode(base64_str)
            video_url = f'{request.cookies.get("account")} - {secrets.token_hex(16)}.mp4'
            try:
                with open(f'static/groups/video/{video_url}', 'wb') as f:
                    f.write(image_binary)
            except:
                return jsonify({'result': False})


            last_post = Post.query.filter_by(user_id=id).order_by(Post.id.desc()).first()
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

@app.route('/new-community')
@check_access
def add_community():
    return render_template('add_group.html')

@app.route('/new-community/add', methods=["POST"])
@check_access
def add_group():
    tag = request.form.get('tag')
    name = request.form.get('name')
    if len(name) < 3:
        return jsonify({'success': False, 'error': 'Имя слишком короткое'})
    if len(tag) < 3:
        return jsonify({'success': False, 'error': 'Тег слишклм короткий'})
    avatar = request.files.get('avatar')
    if avatar:
        avatar.save(f'static/avatars/groups/avatar-group-{tag}.{avatar.filename.split(".")[-1]}')
        avatar_path = f'avatar-group-{tag}.{avatar.filename.split(".")[-1]}'
    else:
        avatar_path = None
    try:
        group = Group(tag=tag, name=name, avatar_path=avatar_path, owner_id=request.cookies.get('account'))
        db.session.add(group)
        db.session.commit()
        return jsonify({'success': True, 'tag': tag})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/<string:tag>', methods=['GET'])
@check_access
def user_profile(tag):
    if request.method == "GET":
        user = User.query.filter_by(tag=tag).first()
        if not user:
            return 'Страницы не существует!'
        self_user_tag = User.query.filter_by(id=request.cookies.get('account')).first().tag

        notifications, notifications_count = check_notification(request.cookies.get('account'))

        month_data = {
            '01': 'января',
            '02': 'февраля',
            '03': 'марта',
            '04': 'апреля',
            '05': 'мая',
            '06': 'июня',
            '07': 'июля',
            '08': 'августа',
            '09': 'сентября',
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

        profile_open = Setting.query.filter_by(user_id=user.id).first().profile_open
        if profile_open == 0:
            isFriend1 = Friends.query.filter_by(user_id=request.cookies.get('account')).filter_by(friend_id=user.id).first()
            if isFriend1:
                profile_open = 1
            if user.id == int(request.cookies.get('account')):
                profile_open = 1

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
                               profile_open=profile_open,
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
                           isSubscribe=isSubscribe,
                           owner=owner
    )



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/post/like', methods=['POST'])
@app.route('/community/post/like', methods=['POST'])
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
        isGroup = request.json.get('isGroup')
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
            if not isGroup:
                user_id = User.query.filter_by(tag=request.json.get('tag')).first().id
            else:
                user_id = Group.query.filter_by(tag=request.json.get('tag')).first().id
            if not isGroup:
                posts = Post.query.filter_by(user_id=user_id).filter_by(isGroup=None).order_by(Post.id.desc()).offset(startWith).limit(count).all()
            else:
                posts = Post.query.filter_by(user_id=user_id).filter_by(isGroup='1').order_by(Post.id.desc()).offset(startWith).limit(count).all()



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
        groups = []
        comments = []
        owners = []
        for post in posts:
            if post.isGroup == '1':
                groups.append(True)
            else:
                groups.append(False)

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
                group = Group.query.filter_by(id=post.user_id).first()
                if (group.owner_id == int(request.cookies.get('account'))):
                    selfs.append(1)
                else:
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
            'liked': liked,
            'groups': groups
        }

        if posts:
            return jsonify(posts_json)
        else:
            return jsonify({'success': False})
    return 'Страница не найдена'

@app.route('/post/remove', methods=['POST'])
@app.route('/community/post/remove', methods=['POST'])
def removePost():
    if request.method == 'POST':
        post_id = int(request.json.get('id'))

        try:
            post = Post.query.filter_by(id=post_id).first()

            if post:
                likes = Likes.query.filter_by(post_id=post_id).all()
                for like in likes:
                    db.session.delete(like)

                if int(request.cookies.get('account')) == post.user_id:
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
        if Setting.query.filter_by(user_id=friend_id).first().notification_friend_request != 0:
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
    friend_id = int(request.cookies.get('account'))
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


            if Setting.query.filter_by(user_id=user_id).first():
                if Setting.query.filter_by(user_id=user_id).first().notification_friend_access != 0:
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

    if str(photo.user_id) == request.cookies.get('account'):
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
    else:
        socketio.emit('deletePhoto_result', {'success': False, 'error': 'Фото не ваше'},
                  room=request.cookies.get('account'))


@app.route('/video/delete', methods=['POST'])
def delete_video():

    video_id = request.json.get('video_id')

    video = Video.query.filter_by(id=video_id).first()

    if video:
        try:
            db.session.delete(video)
            db.session.commit()
            if video.inPost == 'False':
                os.remove(f'static/users/video/{video.path_name}')
            return jsonify({'success': True})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})

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


@app.route('/search-small', methods=['POST'])
def search_small():
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
