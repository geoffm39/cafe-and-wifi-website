from flask import Flask
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

from app import routes, models
