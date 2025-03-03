from flask import Blueprint,render_template,redirect,request
import mysql.connector

bp = Blueprint('login', __name__, template_folder='templates')

@bp.route('/')
def login():
    return render_template('login.html')

@bp.route('/register')
def register():
    return render_template('register.html')