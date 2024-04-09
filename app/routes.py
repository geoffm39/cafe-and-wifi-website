from flask import render_template, redirect, url_for, flash, abort
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from functools import wraps
from app import app, login_manager, db
from gravatar import get_gravatar_url
from app.models import User, Cafe
from app.forms import LoginForm, RegisterForm, AddCafeForm, CommentForm


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        email = form.email.data
        existing_user = db.session.execute(db.Select(User).where(email == User.email)).scalar()
        if existing_user:
            flash('Email already exists, please login')
            return redirect(url_for('login'))
        avatar_url = get_gravatar_url(email)
        new_user = User(email=email,
                        password=hashed_password,
                        avatar_url=avatar_url)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.Select(User).where(User.email == form.email.data)).scalar()
        if not user:
            flash('Wrong email. Try again')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, form.password.data):
            flash('Wrong password. Try again')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/suggest-place')
def suggest_place():
    return render_template('suggest_place.html')


@app.route('/explore')
def explore():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    return render_template('explore.html', cafes=cafes)


@app.route('/contact')
def contact():
    return render_template('contact.html')
