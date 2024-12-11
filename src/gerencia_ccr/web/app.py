from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import openai
from pathlib import Path

from .routes.auth import init_auth_routes
from .routes.reservation import init_reservation_routes
from .routes.video import init_video_routes
from .routes.infantil import init_infantil_routes
from .routes.media import init_media_routes

# Load environment variables from the root directory
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
print(f"Looking for .env file at: {env_path}")
print(f"Does .env file exist? {env_path.exists()}")

# Load environment variables
load_dotenv(dotenv_path=env_path)

# Print all environment variables (excluding sensitive data)
# print("\nEnvironment variables loaded:")
# for key in os.environ:
#     if key in ['MONGO_URI', 'JWT_SECRET_KEY', 'OPENAI_API_KEY']:
#         print(f"{key}: {'*' * 10}")
#     else:
#         print(f"{key}: {os.environ[key]}")

app = Flask(__name__, static_url_path='', static_folder='../../../static')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.debug = True

# Initialize extensions
jwt = JWTManager(app)

# Print MongoDB URI (masked)
mongodb_uri = os.getenv('MONGO_URI')  
if mongodb_uri:
    # Mask the password in the URI for logging
    masked_uri = mongodb_uri.replace('//', '//***:***@') if '@' in mongodb_uri else mongodb_uri
    print(f"\nMongoDB URI found: {masked_uri}")
else:
    print("\nMongoDB URI not found in environment variables")
    print("Current working directory:", os.getcwd())
    print("Environment file path:", env_path)

# Initialize MongoDB client with error handling
try:
    if not mongodb_uri:
        raise ValueError("MongoDB URI is not set in environment variables")
        
    mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    # Verify the connection
    mongo_client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Set the database
    db = mongo_client['gerenciaccr']
    
    # Add collections to app config
    app.config['users_collection'] = db.users
    
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")
    mongo_client = None

# OpenAI Configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# CORS configuration
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:7770", "http://127.0.0.1:7770", "https://sterling-jolly-sailfish.ngrok-free.app"],
         "allow_credentials": True
     }},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Add debug logging for requests
# @app.before_request
# def log_request_info():
#     print('Headers:', dict(request.headers))
#     print('Body:', request.get_data().decode())

# @app.after_request
# def after_request(response):
#     print('Response:', response.status)
#     return response

# Static routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/templates/<path:filename>')
def serve_template(filename):
    return send_from_directory(os.path.join(app.static_folder, 'templates'), filename)

@app.route('/static/<path:filename>')
def serve_static_root(filename):
    return send_from_directory(app.static_folder, filename)

# Initialize routes
init_auth_routes(app, mongo_client['gerenciaccr'])
init_reservation_routes(app, mongo_client['gerenciaccr'])
video_bp = init_video_routes(mongo_client['gerenciaccr'].services)
app.register_blueprint(video_bp)
init_infantil_routes(app, mongo_client['gerenciaccr'].services)
init_media_routes(app, mongo_client['gerenciaccr'].services)

if __name__ == "__main__":
    app.run(debug=True, port=5050, host='0.0.0.0')
