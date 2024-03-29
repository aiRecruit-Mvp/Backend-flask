import os

from flask import request, jsonify, redirect
from flask.cli import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required
from flask_restx import Resource, fields
from user import app, api, mongo, CLIENT_ID, CLIENT, URL_DICT, DATA
from user.models import User
from user.auth import verify_password, generate_random_code, send_email, hash_password
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from oauthlib import oauth2


# Define models for request and response payloads
user_model = api.model('User', {
    'email': fields.String(required=False, description='User email'),
   # 'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'name': fields.String(required=False, description='First name'),
    #'last_name': fields.String(required=False, description='Last name')
})

signup_response_model = api.model('SignupResponse', {
    'name': fields.String(required=True, description='name'),
    'email': fields.String(required=True, description='email'),
    'password': fields.String(required=True, description='Password')
})
# Model specifically for the signin endpoint
signin_model = api.model('Signin', {
    'email': fields.String(required=True, description='email'),
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
    def post(self):
        """Create a new user"""
        json_data = request.json
        email = json_data.get('email')
        password = json_data.get('password')
        name = json_data.get('name')

        if not (email and password and name):
            return {'message': 'Missing information'}, 400

        # Check if the email already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            return {'message': 'Email already exists'}, 400

        # Use the static method to create a user and get the user data including _id
        user_data = User.create_user(email, password, name)

        return user_data, 201

@api.route('/signin')
class Signin(Resource):
    @api.expect(signin_model, validate=True)
    def post(self):
        """Sign in user"""
        json_data = request.json
        email = json_data.get('email')
        password = json_data.get('password')

        # Authenticate the user
        user = User.find_by_email(email)
        if user and verify_password(user['password'], password):
            access_token = create_access_token(identity=email)
            user_data = {
                "name": user['name'],
                "email": user['email'],
                "_id": str(user['_id'])  # Convert ObjectId to string if using MongoDB
            }
            return {"token": access_token, "user": user_data}, 200
        else:
            return {'error': 'Invalid credentials'}, 401


@api.route('/users')
class UserList(Resource):
    @jwt_required()
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

            # Generate a new verification code
            new_verification_code = generate_random_code()

            # Store the new verification code in the database
            mongo.db.password_reset_codes.insert_one({'email': email, 'code': new_verification_code})

            # Send an email with the new verification code to the user
            subject = "Password Reset Verification Code"
            body = f"Your new verification code is: {new_verification_code}"
            send_email(email, subject, body)

            return {'message': 'New verification code sent to your email'}, 200

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
            mongo.db.password_reset_codes.delete_one({'email': email, 'code': code})

            return {'message': 'Password reset successful'}, 200




def exchange_token(code):
    try:
        # Exchange the authorization code for an ID token
        id_token_info = id_token.verify_oauth2_token(
            code,
            google_requests.Request(),
            CLIENT_ID
        )

        # Verify the issuer
        if id_token_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # Return the ID token info
        return id_token_info

    except ValueError as e:
        print("Error verifying ID token:", str(e))
        return None
@app.route('/google-sign-in', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Process the POST request data here
        pass

    if request.is_json:
        code = request.get_json().get('code')
    else:
        code = request.form.get('code')

    print(code)

    if not code:
        # Redirect to the Google Sign-In link if the 'code' parameter is missing
        google_signin_url = CLIENT.prepare_request_uri(
            URL_DICT['google_oauth'],
            redirect_uri=DATA['redirect_uri'],
            scope=DATA['scope'],
            prompt=DATA['prompt']
        )
        return redirect(google_signin_url)

    # Exchange authorization code for ID token
    id_token_info = exchange_token(code)

    if id_token_info is None:
        return "Error during token exchange"

    print(id_token_info)

    # Extract necessary information from the ID token info
    email = id_token_info.get('email')
    sub = id_token_info.get('sub')  # Google user ID

    # You can now store or retrieve user data from MongoDB as needed
    # For example, you may want to save the user information to your database
    user_data = {
        'name': id_token_info.get('name', ''),
        'email': email,
        'google_id': sub
    }
    mongo.db.user.insert_one(user_data)

    return redirect('/user/%s' % email)
