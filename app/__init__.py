from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_restx import Api
from flask_mail import Mail
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
api = Api(app)
mail = Mail(app)
# Initialize the JWTManager with your Flask app
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



from app import routes
