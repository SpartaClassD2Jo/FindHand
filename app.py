from pymongo import MongoClient
from bs4 import BeautifulSoup
from db import client
from flask import Flask, render_template, request, jsonify,session, make_response
from jinja2 import Template
import requests
import jwt


# 나중에 git-encrypt 사용하여 이부분은 따로 보안 할 예정
#client = MongoClient('mongodb+srv://데이타 베이스 넣기')
client = MongoClient('mongodb+srv://test:sparta@cluster0.onepf4f.mongodb.net/?retryWrites=true&w=majority', 27017)

app = Flask(__name__)
db = client.dbsparta

@app.route('/')
def main():
    animals = list(db.animals.find({}, {"_id": False}))
    return render_template("main.html", animals=animals)

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/submit', methods = ['POST'])
def logging_in():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    find_user = db."the data base".find({'email':email_receive, 'password':password_receive}, {'_id':False})
    return jsonify({'msg':find_user})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)




