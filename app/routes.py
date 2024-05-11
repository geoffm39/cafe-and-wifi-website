from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import or_, and_, func
from functools import wraps
from app import app, login_manager, db
from gravatar import get_gravatar_url
from app.models import User, Cafe, Comment, Rating
from app.forms import LoginForm, RegisterForm, AddCafeForm, CommentForm, ProfileForm, PasswordForm
from utils.boolean_converter import convert_booleans_to_symbols, get_boolean_inputs


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def authenticated_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        return abort(403)

    return wrapper


def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        return abort(403)

    return wrapper


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
        avatar_url = get_gravatar_url(email, size=40)
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
@authenticated_only
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET', 'POST'])
@authenticated_only
def profile():
    profile_image_url = get_gravatar_url(current_user.email, size=300)
    profile_form = ProfileForm(email=current_user.email,
                               name=current_user.name)
    password_form = PasswordForm()
    if profile_form.validate_on_submit() and dict(request.form)['submit'] == 'Update Details':
        current_user.email = profile_form.email.data
        current_user.name = profile_form.name.data
        db.session.commit()
        flash('Profile information updated', category='warning')
        return redirect(url_for('profile'))
    elif password_form.validate_on_submit() and dict(request.form)['submit'] == 'Change Password':
        if check_password_hash(current_user.password, password_form.password.data):
            current_user.password = generate_password_hash(password_form.new_password.data,
                                                           method='pbkdf2:sha256',
                                                           salt_length=8)
            db.session.commit()
            flash('Password changed', category='warning')
        else:
            flash('Wrong password. Try again', category='warning')
        return redirect(url_for('profile'))
    return render_template('profile.html',
                           profile_image_url=profile_image_url,
                           profile_form=profile_form,
                           password_form=password_form)


@app.route('/suggest-place')
@authenticated_only
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
        cafes_page = db.paginate(db.select(Cafe).order_by(sort_column).where(
            or_(
                Cafe.name.ilike(f'%{search}%'),
                Cafe.location.ilike(f'%{search}%')
            )
        ),
            page=page,
            per_page=12)
    else:
        boolean_filters = get_boolean_inputs(search_filters)
        favourite_filter = search_filters.get('favourite')
        if favourite_filter and current_user.is_authenticated:
            favourite_cafe_ids = [cafe.id for cafe in current_user.favourite_cafes]
            cafes_page = db.paginate(db.select(Cafe).order_by(sort_column).filter_by(**boolean_filters)
                                     .filter(Cafe.id.in_(favourite_cafe_ids)),
                                     page=page,
                                     per_page=12)
        else:
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
    is_favourite_cafe = False
    if current_user.is_authenticated:
        is_favourite_cafe = requested_cafe in current_user.favourite_cafes
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
                           comment_form=comment_form,
                           is_favourite_cafe=is_favourite_cafe)


@app.route('/rate-cafe/<int:cafe_id>', methods=['POST'])
def rate_cafe(cafe_id):
    if current_user.is_authenticated:
        requested_cafe = db.get_or_404(Cafe, cafe_id)
        user_rating = int(request.form.get('rating'))
        current_user_rating = db.session.execute(db.Select(Rating).where(
            and_(
                Rating.user == current_user,
                Rating.cafe == requested_cafe
            ))).scalar()
        if current_user_rating:
            current_user_rating.rating = user_rating
        else:
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


@app.route('/toggle-favourite/<int:cafe_id>', methods=['POST'])
def toggle_favourite(cafe_id):
    if current_user.is_authenticated:
        requested_cafe = db.get_or_404(Cafe, cafe_id)
        if request.form.get('favourite') != 'on':
            current_user.favourite_cafes.remove(requested_cafe)
        else:
            current_user.favourite_cafes.append(requested_cafe)
        db.session.commit()
        return redirect(url_for('view_cafe', cafe_id=cafe_id, **request.args))
    flash('You must login to save favourites', 'warning')
    return redirect(url_for('login'))


@app.route('/contact')
def contact():
    return render_template('contact.html')
