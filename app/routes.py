from flask import request
from flask_restx import Resource, fields
from app import app, api, mongo
from app.models import User
from app.auth import verify_password, generate_random_code, send_email, hash_password

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
forgot_password_model = api.model('ForgotPassword', {
    'email': fields.String(required=True, description='User email')
})
reset_password_model = api.model('ResetPassword', {
    'email': fields.String(required=True, description='User email'),
    'code': fields.String(required=True, description='Verification code'),
    'new_password': fields.String(required=True, description='New password')
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

    @api.route('/forgot_password')
    class ForgotPassword(Resource):
        @api.expect(forgot_password_model, validate=True)
        def post(self):
            """Forgot password"""
            email = request.json.get('email')

            # Check if the email exists
            user = User.find_by_email(email)
            if not user:
                return {'error': 'Email not found'}, 404

            # Generate a random verification code
            verification_code = generate_random_code()

            # Store the verification code in the database
            mongo.db.password_reset_codes.insert_one({'email': email, 'code': verification_code})

            # Send an email with the verification code to the user
            subject = "Password Reset Verification Code"
            body = f"Your verification code is: {verification_code}"
            send_email(email, subject, body)

            return {'message': 'Verification code sent to your email'}, 200
@api.route('/reset_password')
class ResetPassword(Resource):
    @api.expect(reset_password_model, validate=True)
    def post(self):
        """Reset password"""
        email = request.json.get('email')
        code = request.json.get('code')
        new_password = request.json.get('new_password')

        # Check if the code matches the one stored in the database
        stored_code = mongo.db.password_reset_codes.find_one({'email': email, 'code': code})
        if not stored_code:
            return {'error': 'Invalid verification code'}, 400

        # Update the user's password
        hashed_password = hash_password(new_password)
        mongo.db.users.update_one({'email': email}, {'$set': {'password': hashed_password}})

        # Delete the verification code from the database
        mongo.db.password_reset_codes.delete_one({'email': email})

        return {'message': 'Password reset successful'}, 200
