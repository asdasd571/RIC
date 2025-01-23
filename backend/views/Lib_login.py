###################################################################
#login 일괄 수정 -> db 연동되게 
from flask import Blueprint, request, jsonify,session
from flask_sqlalchemy import SQLAlchemy
import jwt
from ..models import User
from werkzeug.utils import redirect
from .. import db
# SQLAlchemy DB 객체 생성


# User 모델 정의

# Blueprint 설정
ap = Blueprint('login', __name__, url_prefix='/login')

SECRET_KEY = "1005"

# 로그인 처리
@ap.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if request.method == 'GET':
        message = 'GET Echo'
    else:
        # SQLAlchemy로 데이터 조회
        user = User.query.filter_by(username=username).first()

        if user:
            if password == user.password:
                message = 'Login OK'
                data = {"username": username, "password": password, "message": message}
                token = jwt.encode(data, SECRET_KEY, algorithm='HS256')
                return jsonify({'data': data, 'token': token}),201
            else:
                message = 'Password Fail'
                print("비밀번호 확인 부분을 다시 작성해주세요")
        else:
            message = "Unknown User"
            print("회원가입을 해주세요")
    message = 'error'
    data = {"username": username, "password": password, "message": message}
    return jsonify(data),400  # Error case

# 회원가입 처리
@ap.route('/register', methods=['GET'])
def register_get():
    username = request.args.get('username')
    # password = request.args.get('password')

    # SQLAlchemy로 데이터 조회
    user = User.query.filter_by(username=username).first()

    if user:
        message = 'GET OK'
        email = user.email
    else:
        message = 'Unknown user'
        email = None

    #password 삭제 - 보안 GET 요청시 패스워드 쿼리 스트링에 있는 것은 매우 좋지 않음
    data = {"username": username, "email": email, "message": message}
    return jsonify(data)

@ap.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']

    if password != password2:
        message = 'Password mismatch'
        print("비밀 번호를 다시 확인해주세요")
        return jsonify({"message": message})

    # SQLAlchemy로 데이터 조회
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        message = 'Username already taken'
        print("이미 존재하는 회원입니다")
        return jsonify({"message": message})

    # 새로운 사용자 추가
    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()

    message = 'Registration successful'
    print("회원가입 완료!")
    data = {"username": username, "email": email, "message": message}
    return jsonify(data)

# 회원탈퇴 처리
@ap.route('/deregister', methods=['GET', 'DELETE'])
def deregister():
    username = request.form['username']
    password = request.form['password']

    if request.method == 'GET':
        message = 'GET OK'
    else:
        # SQLAlchemy로 데이터 조회
        user = User.query.filter_by(username=username).first()

        if user:
            stored_password = user.password
            if password == stored_password:
                db.session.delete(user)
                db.session.commit()
                message = 'Delete OK'
            else:
                message = 'Password Fail'
        else:
            message = "No user exists"

    data = {"username": username, "message": message}
    return jsonify(data)

# 로그아웃 처리
@ap.route('/logout')
def logout():
    username = session.get('username')
    session.pop(username, None)
    return redirect('/')
###################################################################
