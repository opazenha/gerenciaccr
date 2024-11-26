from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/gerenciaccr")
        _client = MongoClient(mongo_uri)
        _db = _client.gerenciaccr
    return _db

def init_db(app=None):
    db = get_db()
    # Initialize collections
    if app is not None:
        app.config['users_collection'] = db['users']
        app.config['rooms_collection'] = db['rooms']
        app.config['reservations_collection'] = db['reservations']
        app.config['services_collection'] = db['services']
    return db

# For backwards compatibility
users_collection = get_db()['users']
rooms_collection = get_db()['rooms']
reservations_collection = get_db()['reservations']
services_collection = get_db()['services']
