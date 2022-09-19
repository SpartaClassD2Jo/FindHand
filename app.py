from pymongo import MongoClient
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify,session, make_response
from jinja2 import Template
import jwt

app = Flask(__name__)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
