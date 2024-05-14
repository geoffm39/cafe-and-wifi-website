from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_, func
from functools import wraps
from app import app, login_manager, db
from gravatar import get_gravatar_url
from app.models import User, Cafe, Comment, Rating
from app.forms import LoginForm, RegisterForm, AddCafeForm, CommentForm, ProfileForm, PasswordForm, ContactForm
from utils.boolean_converter import convert_booleans_to_symbols, get_boolean_inputs
from utils.email import send_email


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
        if current_user.is_admin():
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
                        name=form.name.data,
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


@app.route('/edit/<int:cafe_id>', methods=['GET', 'POST'])
@admin_only
def edit_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    edit_form = AddCafeForm(name=requested_cafe.name,
                            location=requested_cafe.location,
                            map_url=requested_cafe.map_url,
                            image_url=requested_cafe.img_url,
                            seats=requested_cafe.seats,
                            coffe_price=requested_cafe.coffee_price,
                            has_sockets=requested_cafe.has_sockets,
                            has_toilet=requested_cafe.has_toilet,
                            has_wifi=requested_cafe.has_wifi,
                            can_take_calls=requested_cafe.can_take_calls)
    if edit_form.validate_on_submit():
        form_cafe_name = edit_form.name.data
        existing_cafe = db.session.execute(db.Select(Cafe).where(Cafe.name == form_cafe_name)).scalar()
        if existing_cafe:
            flash('Cafe name already exists', 'warning')
            return redirect(url_for('edit_cafe', cafe_id=requested_cafe.id))
        requested_cafe.name = form_cafe_name
        requested_cafe.location = edit_form.location.data
        requested_cafe.map_url = edit_form.map_url.data
        requested_cafe.img_url = edit_form.image_url.data
        requested_cafe.seats = edit_form.seats.data
        requested_cafe.coffee_price = edit_form.coffee_price.data
        requested_cafe.has_sockets = edit_form.has_sockets.data
        requested_cafe.has_toilet = edit_form.has_toilet.data
        requested_cafe.has_wifi = edit_form.has_wifi.data
        requested_cafe.can_take_calls = edit_form.can_take_calls.data
        db.session.commit()
        return redirect(url_for('view_cafe', cafe_id=requested_cafe.id))
    return render_template('suggest_place.html', cafe_form=edit_form, is_edit=True)


@app.route('/delete/<int:cafe_id>', methods=['GET', 'POST'])
@admin_only
def delete_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(requested_cafe)
    db.session.commit()
    return redirect(url_for('explore'))


@app.route('/suggest-place', methods=['GET', 'POST'])
@authenticated_only
def suggest_place():
    cafe_form = AddCafeForm()
    if cafe_form.validate_on_submit():
        cafe_name = cafe_form.name.data
        existing_cafe = db.session.execute(db.Select(Cafe).where(cafe_name == Cafe.name)).scalar()
        if existing_cafe:
            flash('Cafe already exists', 'warning')
            return redirect(url_for('suggest_place'))
        suggested_cafe = Cafe(name=cafe_name,
                              map_url=cafe_form.map_url.data,
                              img_url=cafe_form.image_url.data,
                              location=cafe_form.location.data,
                              has_sockets=cafe_form.has_sockets.data,
                              has_toilet=cafe_form.has_toilet.data,
                              has_wifi=cafe_form.has_wifi.data,
                              can_take_calls=cafe_form.can_take_calls.data,
                              seats=cafe_form.seats.data,
                              coffee_price=cafe_form.coffee_price.data)
        db.session.add(suggested_cafe)
        db.session.commit()
        new_cafe = db.session.execute(db.Select(Cafe).where(cafe_name == Cafe.name)).scalar()
        return redirect(url_for('view_cafe', cafe_id=new_cafe.id))
    return render_template('suggest_place.html', cafe_form=cafe_form)


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


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        name = contact_form.name.data
        email = contact_form.email.data
        subject = contact_form.subject.data
        message = contact_form.message.data
        email_message = f'Name: {name}\nEmail: {email}\n{message}'
        send_email('geoffm39@gmail.com', subject, email_message)
        flash('Message Sent. We will get back to you soon!', 'warning')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=contact_form)
