from flask import Flask
from flask_pymongo import PyMongo
from flask_restx import Api

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
api = Api(app)
from app import routes
