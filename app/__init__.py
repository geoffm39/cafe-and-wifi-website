from flask import Flask
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)

from app import routes
