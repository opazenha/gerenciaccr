from flask import current_app
from bson import ObjectId

class UserModel:
    def __init__(self):
        self.users_collection = current_app.config['users_collection']

    def get_user_by_id(self, user_id):
        """Get user by ID from the database."""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return user
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None