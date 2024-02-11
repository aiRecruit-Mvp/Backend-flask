import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_restx import Api
from flask_mail import Mail
from oauthlib import oauth2
from dotenv import load_dotenv
from flask_cors import CORS


from config import Config
load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
api = Api(app)
mail = Mail(app)
# Initialize the JWTManager with your Flask user
jwt = JWTManager(app)


# Callback function to check if a token is missing
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'authorization_required',
        'message': 'Authorization token is missing'
    }), 401


# Callback function to handle expired tokens
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'token_expired',
        'message': 'The token has expired'
    }), 401


# Callback function to handle invalid tokens
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'invalid_token',
        'message': 'Signature verification failed.'
    }), 422  # 422 Unprocessable Entity for semantic correctness


# Callback function for tokens that are not fresh if you are using fresh tokens
@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'fresh_token_required',
        'message': 'Fresh token is required.'
    }), 401


# Callback function to handle revoked tokens
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'token_revoked',
        'message': 'The token has been revoked.'
    }), 401


@jwt.unauthorized_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "authorization_required",
        "message": "Missing Authorization Header"
    }), 401
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

DATA = {
    'response_type': "code",
    'redirect_uri': "https://localhost:5000/home",
    'scope': 'https://www.googleapis.com/auth/userinfo.email',
    'client_id': CLIENT_ID,
    'prompt': 'consent'
}


URL_DICT = {
    'google_oauth': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_gen': 'https://oauth2.googleapis.com/token',
    'get_user_info': 'https://www.googleapis.com/oauth2/v3/userinfo'
}

CLIENT = oauth2.WebApplicationClient(CLIENT_ID)


from user import routes
