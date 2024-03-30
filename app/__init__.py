from flask import Flask
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from flask_ckeditor import CKEditor
import os

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)


from app import routes
