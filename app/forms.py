from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    occupation = StringField('Occupation')
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AddCafeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    map_url = StringField('Map URL', validators=[DataRequired(), URL()])
    image_url = StringField('Image URL', validators=[DataRequired(), URL()])
    seats = StringField('Seats', validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    has_sockets = BooleanField('Has Sockets', validators=[DataRequired()])
    has_toilet = BooleanField('Has Toilet', validators=[DataRequired()])
    has_wifi = BooleanField('Has Wifi', validators=[DataRequired()])
    can_take_calls = BooleanField('Can Take Calls', validators=[DataRequired()])
    submit = SubmitField('Add Cafe')


class CommentForm(FlaskForm):
    comment = CKEditorField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
