from flask import request
from flask_restx import Resource, fields
from app import app, api, mongo
from app.models import User
from app.auth import verify_password

# Define models for request and response payloads
user_model = api.model('User', {
    'email': fields.String(required=False, description='User email'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'name': fields.String(required=False, description='First name'),
    'last_name': fields.String(required=False, description='Last name')
})

signup_response_model = api.model('SignupResponse', {
    'message': fields.String(description='Message'),
    'user_id': fields.String(description='User ID')
})
# Model specifically for the signin endpoint
signin_model = api.model('Signin', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})
# Define API routes using Flask-RESTx
@api.route('/signup')
class Signup(Resource):
    @api.expect(user_model, validate=True)
    @api.marshal_with(signup_response_model, code=201)
    def post(self):
        """Create a new user"""
        json_data = request.json
        email = json_data.get('email')
        username = json_data.get('username')
        password = json_data.get('password')
        name = json_data.get('name')
        last_name = json_data.get('last_name')

        if not (email and username and password and name and last_name):
            return {'message': 'Missing information'}, 400

        # Check if the email already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return {'message': 'Email already exists'}, 400

        # Create the user
        user_id = User.create_user(email, username, password, name, last_name)
        return {'message': 'User created successfully', 'user_id': user_id}, 201
@api.route('/signin')
class Signin(Resource):
    @api.expect(signin_model, validate=True)
    def post(self):
        """Sign in user"""
        json_data = request.json
        username = json_data.get('username')
        password = json_data.get('password')

        if not (username and password):
            return {'error': 'Missing username or password'}, 400

        user = User.find_by_username(username)
        if user and verify_password(user['password'], password):
            return {'message': 'Login successful'}, 200
        else:
            return {'error': 'Invalid credentials'}, 401

@api.route('/users')
class UserList(Resource):
    def get(self):
        """List all users"""
        users = User.find_all(mongo.db)
        serialized_users = []
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            serialized_users.append(user)
        return serialized_users, 200