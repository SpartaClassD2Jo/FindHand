from pymongo import MongoClient
from bs4 import BeautifulSoup
from db import clie
from flask import Flask, render_template, request, jsonify,session, make_response
from jinja2 import Template
import jwt


# 나중에 git-encrypt 사용하여 이부분은 따로 보안 할 예정
client = MongoClient('mongodb+srv://데이타 베이스 넣기')

app = Flask(__name__)
db = client.dbsparta

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/submit', methods = ['POST'])
def logging_in():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    find_user = db."the data base".find({'email':email_receive, 'password':password_receive}, {'_id':False})
    return jsonify({'msg':find_user})



@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
