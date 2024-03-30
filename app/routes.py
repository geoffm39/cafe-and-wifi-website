from flask import render_template, redirect, url_for, flash, abort
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from functools import wraps

from app import app
from app.forms import LoginForm, RegisterForm, AddCafeForm, CommentForm


@app.route('/')
def home():
    return render_template('index.html')
