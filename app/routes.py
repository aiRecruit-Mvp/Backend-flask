from flask import request, jsonify
from flask_restx import Resource
from flask_restx import fields

from app import mongo, api
from app.models import User
from app.auth import hash_password, verify_password
# Model for SignUp
signup_model = api.model('SignUp', {
    'email': fields.String(required=True, description='User email address'),
    'username': fields.String(required=True, description='User username'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(required=True, description='User first name'),
    'last_name': fields.String(required=True, description='User last name'),
})

# Model for SignIn
signin_model = api.model('SignIn', {
    'username': fields.String(required=True, description='User username'),
    'password': fields.String(required=True, description='User password'),
})


user_ns = api.namespace('users', description='User operations')

@user_ns.route('/signup')
class Signup(Resource):
    @user_ns.expect(signup_model)  # Expect the signup_model for documentation and validation
    def post(self):
        # json_data = request.json  # This line is no longer needed since we use api.expect
        data = api.payload  # Access validated payload directly
        user_id = User.create_user(**data)  # Unpack data directly into the function call
        return {'message': 'User created successfully', 'user_id': user_id}, 201


@user_ns.route('/signin')
class Signin(Resource):
    @user_ns.expect(signin_model)  # Expect the signin_model for documentation and validation
    def post(self):
        # json_data = request.json  # This line is no longer needed since we use api.expect
        username = api.payload['username']
        password = api.payload['password']

        user = User.find_by_username(username)
        if user and verify_password(user['password'], password):
            return {'message': 'Login successful'}, 200
        else:
            return {'error': 'Invalid credentials'}, 401


@user_ns.route('/')
class Users(Resource):
    def get(self):
        users = User.find_all(mongo.db)
        serialized_users = []
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            serialized_users.append(user)
        return serialized_users, 200
