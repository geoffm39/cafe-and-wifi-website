from flask import Flask
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
import os

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)

# gravatar = Gravatar(app,
#                     size=100,
#                     rating='g',
#                     default='retro',
#                     force_default=False,
#                     force_lower=False,
#                     use_ssl=False,
#                     base_url=None)


from app import routes
