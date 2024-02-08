from app import mongo
from app.auth import hash_password, verify_password


class User:
    def __init__(self, email, username, password, name, last_name):
        self.email = email
        self.username = username
        self.password = password  # This should be hashed before storing
        self.name = name
        self.last_name = last_name

    @staticmethod
    def create_user(email, username, password, name, last_name):
        """
        Creates a new user document in the MongoDB database.
        """
        hashed_password = hash_password(password)
        user_data = {
            'email': email,
            'username': username,
            'password': hashed_password,
            'name': name,
            'last_name': last_name
        }
        result = mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)

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
