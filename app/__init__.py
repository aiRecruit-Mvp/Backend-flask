from flask import Flask
from flask_pymongo import PyMongo
from flask_restx import Api
from flask_mail import Mail
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
api = Api(app)
mail = Mail(app)

from app import routes
