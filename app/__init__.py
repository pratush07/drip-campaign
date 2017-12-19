from flask import Flask
from pytz import timezone
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import uuid
import os

# for using http redirects instead of https..
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = str(uuid.uuid4())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
db = SQLAlchemy(app)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
#add your timezone 
my_tz = timezone('Asia/Kolkata')
CLIENT_SECRETS_FILE = "XXXXX.json"
SCOPES = ['https://mail.google.com/','https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/userinfo.email']

from app import views