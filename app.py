from pymongo import MongoClient
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify,session, make_response
from jinja2 import Template
import jwt
from requests import get
import requests
import hashlib
import datetime
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
url = "https://www.animal.go.kr/front/awtis/protection/protectionList.do?totalCount=6267&pageSize=10&menuNo=1000000060&&"

data = requests.get(url,headers=headers)

soup = BeautifulSoup(data.text,'html.parser')


# 나중에 git-encrypt 사용하여 이부분은 따로 보안 할 예정
client = MongoClient('mongodb+srv://test:sparta@cluster0.o2cbi29.mongodb.net/Cluster0?retryWrites=true&w=majority')
# database 이름은 "weekone"
# client = MongoClient('mongodb+srv://sparta:sparta@cluster0.kuzlucm.mongodb.net/?retryWrites=true&w=majority')
app = Flask(__name__)
db = client.dbsparta


# 로그인 페이지 보여주는 API
@app.route('/login')
def login():
    return render_template('login.html')

# 회원 가입 페이지 보여주는 API
@app.route('/register')
def register_page():
    return render_template('register.html')


# 이메일 중복확인 API

@app.route('/register/duplicate', methods = ['POST'])
def check_duplicate():
    email = request.form['email_give']
    print(email)
    existing_user = bool(list(db.weekone.find({'email':email})))
    print(existing_user)
    if existing_user:
        return jsonify({'msg':'이미 사용중인 아이디입니다'})
    else:
        return jsonify({'msg':'사용 가능한 아이디입니다'})


# 회원 가입 API
@app.route('/register/newUser', methods =['POST'])
def register_newuser():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "email" : email_receive,
        "password" : pw_hash
    }
    db.weekone.insert_one(doc)
    return jsonify({'msg':'회원 가입 완료!'})


# 로그인 눌렀을때 API
@app.route('/login/submit', methods = ['POST'])
def logging_in():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    find_user = db.weekone.find({'email':email_receive, 'password':password_receive}, {'_id':False})
    return jsonify({'msg':find_user})



@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
