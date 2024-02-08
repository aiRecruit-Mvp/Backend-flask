from flask import request, jsonify
from app import app, mongo
from app.models import User
from app.auth import hash_password, verify_password

@app.route('/signup', methods=['POST'])
def signup():
    json_data = request.json
    email = json_data.get('email')
    username = json_data.get('username')
    password = json_data.get('password')
    name = json_data.get('name')
    last_name = json_data.get('last_name')

    if not (email and username and password and name and last_name):
        return jsonify({'error': 'Missing information'}), 400

    # Optional: Add logic to check if user already exists

    user_id = User.create_user(email, username, password, name, last_name)
    return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201

@app.route('/signin', methods=['POST'])
def signin():
    json_data = request.json
    username = json_data.get('username')
    password = json_data.get('password')

    if not (username and password):
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.find_by_username(username)
    if user and verify_password(user['password'], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


from bson import ObjectId

@app.route('/users', methods=['GET'])
def list_users():
    users = User.find_all(mongo.db)
    serialized_users = []
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        serialized_users.append(user)
    return jsonify(serialized_users), 200
