from pymongo import MongoClient
from bson.objectid import ObjectId
from bs4 import BeautifulSoup
import certifi
from jinja2 import Template
import requests
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = 'SPARTA'
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.onepf4f.mongodb.net/?retryWrites=true&w=majority', 27017,
                     tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        animals = list(db.animals.find({}))
        user = db.users.find_one({'username': payload['id']})
        return render_template("main.html", animals=animals, nickname = user['nickname']  )


    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 메인 페이지 landing 시에 유저 정보 가져오는 API



@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# 회원 가입 페이지 보여주는 API
@app.route('/register')
def register_page():
    return render_template('register.html')


# 이메일 중복확인 API

@app.route('/register/duplicate', methods=['POST'])
def check_duplicate():
    email = request.form['username_give']
    print(email)
    existing_user = bool(list(db.users.find({'user': email})))
    print(existing_user)
    if existing_user:
        return jsonify({'msg': '이미 사용중인 아이디입니다'})
    else:
        return jsonify({'msg': '사용 가능한 아이디입니다'})


# 회원 가입 API
@app.route('/register/newUser', methods=['POST'])
def register_newuser():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": email_receive,
        "password": pw_hash,
        "nickname": nickname_receive
    }
    db.users.insert_one(doc)
    return jsonify({'msg': '회원 가입 완료!'})


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
            'exp': datetime.utcnow() + timedelta(seconds=60 * 5)  # 로그인 5분 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 메인페이지에서 등록하기 버튼을 눌렀을 때
@app.route('/posting')
def posting():
    return render_template('post.html')


@app.route('/animalList')
def main():
    return render_template('animalList.html')

# 메인페이지에서 세부 동물정보 불러오기
@app.route("/detail/<id>")
def postGet(id):
    clickAnimal = list(db.animals.find({'_id': id}))
    print(clickAnimal)
    # return render_template("detail.html",clickAnimal=clickAnimal)


# 글쓰는 페이지에서 등록하기 버튼 누르기
@app.route("/post", methods=["POST"])
def animal_post():
    kind_receive = request.form['kind_give']
    area_receive = request.form['area_give']
    sex_receive = request.form['sex_give']
    info_receive = request.form['info_give']
    url_receive = request.form["url_give"]

    doc = {
        'kind': kind_receive,
        'area': area_receive,
        'sex': sex_receive,
        'info': info_receive,
        'url': url_receive
    }

    db.animal.insert_one(doc)
    return jsonify({'meassage': '등록 완료!'})


# 작성한 글 삭제하기
@app.route("/delete", methods=["POST"])
def deleteAnimal():
    kind_receive = request.form['kind_give']
    area_receive = request.form['area_give']
    sex_receive = request.form['sex_give']
    info_receive = request.form['info_give']
    deleteAnimal = db.animal.find_one({'kind': kind_receive}, {'area': area_receive})
    db.animal.delete_one(deleteAnimal)
    return jsonify({'msg': '삭제 완료!'})

 # 글 수정시 
@app.route("/api/edit", methods=["GET"])
def animal_edit():
    detail_id = request.args.get("id_give")
    animal_details = db.animals.find_one({"_id": ObjectId(detail_id)}, {"_id": False}                                 
    return jsonify({'animal_details': animal_details})

 # 글 수정 후 재등록시  
@app.route("/api/post", methods=["POST"])
def animal_repost():
    detail_id = request.form["id_give"]
    kind_receive = request.form['kind_give']
    area_receive = request.form['area_give']
    sex_receive = request.form['sex_give']
    info_receive = request.form['info_give']

    db.animals.update_many({"_id": ObjectId(detail_id)}, {
        "$set": {'kind': kind_receive, 'area': area_receive, 'sex': sex_receive, 'info': info_receive}})

    animal_details = db.animals.find_one({"_id": ObjectId(detail_id)}, {"_id": False})
    print(animal_details)
    return jsonify({'animal_details': animal_details})                                         
                                         
  
if __name__ == '__main__':
    app.run('0.0.0.0', port=5010, debug=True)
