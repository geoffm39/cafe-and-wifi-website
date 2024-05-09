from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import or_, func
from functools import wraps
from app import app, login_manager, db
from gravatar import get_gravatar_url
from app.models import User, Cafe, Comment, Rating
from app.forms import LoginForm, RegisterForm, AddCafeForm, CommentForm
from utils.boolean_converter import convert_booleans_to_symbols, get_boolean_inputs


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
            flash('Email already exists, please login', 'warning')
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
            flash('Wrong email. Try again', 'warning')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, form.password.data):
            flash('Wrong password. Try again', 'warning')
            return redirect(url_for('login'))
        if form.remember_me.data:
            login_user(user, remember=True)
        else:
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
    page = request.args.get('page', 1, type=int)
    search_filters = request.args.to_dict()
    sort_by = search_filters.get('sort_by')
    sort_column = getattr(Cafe, sort_by) if sort_by else None
    search = search_filters.get('cafe_search')
    if search:
        cafes_page = db.paginate(db.select(Cafe).order_by(sort_column).where(or_(
            Cafe.name.ilike(f'%{search}%'),
            Cafe.location.ilike(f'%{search}%')
        )),
            page=page,
            per_page=12)
    else:
        boolean_filters = get_boolean_inputs(search_filters)
        cafes_page = db.paginate(db.select(Cafe).order_by(sort_column).filter_by(**boolean_filters),
                                 page=page,
                                 per_page=12)
    cafe_dictionaries = [cafe.to_dict() for cafe in cafes_page]
    for cafe in cafe_dictionaries:
        convert_booleans_to_symbols(cafe)
    return render_template('explore.html', pagination=cafes_page, cafes=cafe_dictionaries)


@app.route('/cafe/<int:cafe_id>', methods=['GET', 'POST'])
def view_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    cafe_dictionary = requested_cafe.to_dict()
    convert_booleans_to_symbols(cafe_dictionary)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(text=comment_form.comment.data,
                              user=current_user,
                              cafe=requested_cafe)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('view_cafe', cafe_id=requested_cafe.id))
        return redirect(url_for('login'))
    return render_template('cafe.html',
                           cafe=cafe_dictionary,
                           comment_form=comment_form)


@app.route('/rating/<int:cafe_id>', methods=['POST'])
def rate_cafe(cafe_id):
    if current_user.is_authenticated:
        requested_cafe = db.get_or_404(Cafe, cafe_id)
        user_rating = int(request.form.get('rating'))
        rating = Rating(rating=user_rating,
                        user=current_user,
                        cafe=requested_cafe)
        db.session.add(rating)
        db.session.commit()
        requested_cafe.average_rating = db.session.execute(
            db.Select(func.avg(Rating.rating)).where(Rating.cafe_id == cafe_id)).scalar()
        db.session.commit()
        return redirect(url_for('view_cafe', cafe_id=cafe_id))
    flash('You must login to give a rating', 'warning')
    return redirect(url_for('login'))


@app.route('/contact')
def contact():
    return render_template('contact.html')
