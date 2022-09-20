
from pymongo import MongoClient
from bs4 import BeautifulSoup
from db import client

from flask import Flask, render_template, request, jsonify,session, make_response
from jinja2 import Template
import requests

import jwt
import datetime








# 나중에 git-encrypt 사용하여 이부분은 따로 보안 할 예정

# database 이름은 "weekone"

import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
 main

app = Flask(__name__)

SECRET_KEY = 'SPARTA'

from pymongo import MongoClient
import certifi


ca = certifi.where()


client = MongoClient('mongodb+srv://jiae:kja9798!@cluster0.hvkrheo.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta_plus_week4

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 5 )  # 로그인 5분 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5010, debug=True)