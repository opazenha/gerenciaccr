from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv
from app.config.database import init_db, get_db
from app.routes import auth, static, reservation, video, media

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='../static')
    app.debug = True
    
    # CORS Configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5050"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    jwt = JWTManager(app)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(static.bp)
    app.register_blueprint(reservation.bp)
    app.register_blueprint(media.bp)

    # Register video routes
    video_bp = video.init_video_routes(app.config['services_collection'])
    app.register_blueprint(video_bp)

    from app.routes import infantil
    app.register_blueprint(infantil.bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5050)