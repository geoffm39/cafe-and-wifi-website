from flask import render_template, redirect, url_for, flash, abort
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from libgravatar import Gravatar
from functools import wraps

from app import app, login_manager, db
from app.models import User
from app.forms import LoginForm, RegisterForm, AddCafeForm, CommentForm


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/')
def home():
    return render_template('index.html')
