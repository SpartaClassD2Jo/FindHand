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


# 비밀키 세팅
SECRET_KEY = 'SPARTA'
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.onepf4f.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)

db = client.dbsparta

# 메인페이지 접근 API
@app.route('/')
def home():
    # token 받아서 시크릿키를 통해 복호화 진행
    token_receive = request.cookies.get('mytoken')
    try:
        # payload 추출
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # main.html에 전송될 동물 list
        animals = list(db.animals.find({}))
        #  payload id값-> 해당 유저 발견시 매안 화면을 넘겨준디.
        user = db.users.find_one({'username': payload['id']})
        return render_template("main.html", animals=animals, nickname=user['nickname'])

    # 만약 payload에서 설정한 유효시간이 만료됐을 경우.
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # 만약 payload id값을 발견하지 못했을 경우.
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# login 페이지 보여주는  API
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


# 로그인하는 API
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 클라이언트로 부터 username_give, password_give를 받는다.
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # 가입과 같은 방식으로 패스워드 암호화 처리
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 결과를 db에 저장해서 같은 값을 찾아 해당 유저를 찾음.
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # 유저가 존재할 때, 클라이언트에게 토큰 발급
    if result is not None:

        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 5)  # 로그인 5분 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # 토큰에 id와 유효 시간 담은 payload & 시크릿키 다시 암호화 하여 유저에게 전달
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 메인페이지에서 등록하기 버튼을 눌렀을 때
@app.route('/posting')
def posting():
    return render_template('post.html')


# 메인페이지에서 세부 동물정보 불러오기
@app.route("/detail/<id>")
def postGet(id):
    # 메인페이지에서 해당 동물 클릭시 url의 id를 받아서 찾은 후, id에 해당하는 동물 정보를 clickanimal로 전송
    clickAnimal = db.animals.find_one({'_id': ObjectId(id)}, {"_id": False})
    return render_template("detail.html", clickAnimal=clickAnimal)


# 글쓰는 페이지에서 등록하기 버튼 누르기
@app.route("/post", methods=["POST"])
def animal_post():
    # 받은 데이터들을 변수로 저장
    kind_receive = request.form['kind_give']
    area_receive = request.form['area_give']
    sex_receive = request.form['sex_give']
    info_receive = request.form['info_give']
    url_receive = request.form["url_give"]

    # DB의 저장하기 위한 형태로 key값을 붙여줌
    doc = {
        'kind': kind_receive,
        'area': area_receive,
        'sex': sex_receive,
        'info': info_receive,
        'img': url_receive,
        # inputValue를 통해 유기동물보호소와 임시보호 동물을 구분, 임시보호동물의 경우 'inputValue': True
        'inputValue': True
    }

    # doc를 DB에 insert
    db.animals.insert_one(doc)
    return jsonify({'meassage': '등록 완료!'})


# 작성한 글 삭제하기
@app.route("/delete", methods=["GET"])
def delete_animal():
    # detail.html에서 삭제버튼 누를 시, 해당페이지 url에 포함된 id를 전송 받아 detail_id에 넣어준다.
    detail_id = request.args.get("id_give")

    # 받은 id를 이용하여 DB에서 해당 동물의 data를 삭제
    db.animals.delete_one({"_id": ObjectId(detail_id)})
    return jsonify({'msg': '삭제 완료!'})


# 글 수정시
@app.route("/api/edit", methods=["GET"])
def animal_edit():
    # detail.html에서 수정버튼 누를 시, 해당페이지 url에 포함된 id를 전송 받아 detail_id에 넣어준다.
    detail_id = request.args.get("id_give")

    # 받은 id를 이용하여 DB에서 해당 동물의 data를 찾아서 animal_details로 return
    animal_details = db.animals.find_one({"_id": ObjectId(detail_id)}, {"_id": False})
    return jsonify({'animal_details': animal_details})


# 글 수정 후 재등록시
@app.route("/api/post", methods=["POST"])
def animal_repost():
    # 수정 후 등록 버튼을 누를시, 클라이언트에서 전송된 데이터를 받아 각 변수에 넣어준다.
    detail_id = request.form["id_give"]
    kind_receive = request.form['kind_give']
    area_receive = request.form['area_give']
    sex_receive = request.form['sex_give']
    info_receive = request.form['info_give']

    # 받은 detail_id를 이용하여 DB의 동물 정보를 업데이트 해준다.
    db.animals.update_many({"_id": ObjectId(detail_id)}, {
        "$set": {'kind': kind_receive, 'area': area_receive, 'sex': sex_receive, 'info': info_receive}})

    # 업데이트 후 다시 id로 해당 동물의 정보와 메시지를 return
    animal_details = db.animals.find_one({"_id": ObjectId(detail_id)}, {"_id": False})
    return jsonify({'animal_details': animal_details}, {'msg': '수정 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5003, debug=True)
