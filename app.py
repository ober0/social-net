from functools import wraps
import secrets
from flask import Flask, session, url_for, redirect, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from models import db, User
from flask_mail import Mail, Message
from config import app
import random


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
                if str(user.password) == str(request.json.get('password')):
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
        if session.get('auth') != True:
            return redirect('/')
        else:
            return render_template('reg.html', emails=[user.email for user in User.query.all()])

    if request.method == "POST":
        tag = request.json.get('tag')
        email = request.json.get('email')
        password = request.json.get('password')


        session['auth_data'] = f'{tag}:%:%:{email}:%:%:{password}'

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
        print(str(code), str(session['auth_code']))
        if str(code) == str(session['auth_code']):
            print(1)
            data = session.get('auth_data').split(':%:%:')
            user = User(tag=data[0], email=data[1], password=data[2], status=0)
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
                print(e)
                db.session.rollback()

        return jsonify({
            'res': False
        }), 401


@app.route('/exit')
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
        if not User.query.filter_by(tag=tag).first():
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
        return render_template('edit_user.html', user=user)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, allow_unsafe_werkzeug=True)