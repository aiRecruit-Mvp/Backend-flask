from app import mongo
from app.auth import hash_password, verify_password

class User:
    def __init__(self, email, username, password, name):
        self.email = email
        self.username = username
        self.password = password  # This should be hashed before storing
        self.name = name

    @staticmethod
    def create_user(email, password, name):
        """
        Creates a new user document in the MongoDB database.
        """
        hashed_password = hash_password(password)  # Ensure this securely hashes the password
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name,
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
        return user_data

    @staticmethod
    def find_all(db):
        """
        Retrieves all user documents from the MongoDB database.
        """
        users = db.users.find()
        return list(users)
    @staticmethod
    def find_by_username(username):
        """
        Retrieves a user document from the MongoDB database by username.
        """
        user = mongo.db.users.find_one({'username': username})
        return user

    @staticmethod
    def find_by_email(email):
        """
        Retrieves a user document from the MongoDB database by email.
        """
        user = mongo.db.users.find_one({'email': email})
        return user

    @staticmethod
    def verify_user(username, password):
        """
        Verifies if the provided username and password match those stored in the database.
        """
        user = User.find_by_username(username)
        if user and verify_password(user['password'], password):
            return True
        return False
