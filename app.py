from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from routes.video import init_video_routes
import bcrypt
import os
import time

load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='static')
app.debug = True

# OpenAI Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/templates/<path:filename>')
def serve_template(filename):
    return send_from_directory(os.path.join(app.static_folder, 'templates'), filename)

@app.route('/<path:filename>')
def serve_static_root(filename):
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        app.logger.error(f"Error serving {filename}: {str(e)}")
        return f"Error: {str(e)}", 404

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5050"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "your-mongodb-uri-here")
client = MongoClient(MONGO_URI)
db = client.gerenciaccr
users_collection = db['users']
rooms_collection = db['rooms']
reservations_collection = db['reservations']
services_collection = db['services']
videos_collection = db['videos']

@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200
        
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Email e senha são obrigatórios"}), 400

    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            "status": "success",
            "token": access_token,
            "user": {
                "email": user["email"],
                "name": user["name"]
            }
        }), 200
    return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401

@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return "", 200
        
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"status": "error", "message": "Todos os campos são obrigatórios"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"status": "error", "message": "Email já cadastrado"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "email": email,
        "password": hashed_password,
        "name": name
    }
    users_collection.insert_one(user)
    return jsonify({"status": "success", "message": "Usuário registrado com sucesso"}), 201

@app.route("/api/reservations", methods=["POST"])
@jwt_required()
def create_reservation():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    data = request.get_json()
    current_user = get_jwt_identity()
    
    # Get user details for the reservation
    user = users_collection.find_one({"_id": ObjectId(current_user)})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Check for existing reservations in the same location and time
    existing = reservations_collection.find_one({
        "date": data['date'],
        "location": data['location'],
        "$or": [
            {
                "startTime": {"$lt": data['endTime']},
                "endTime": {"$gt": data['startTime']}
            },
            {
                "startTime": data['startTime'],
                "endTime": data['endTime']
            }
        ]
    })

    if existing:
        # Get the user who created the conflicting reservation
        conflict_user = users_collection.find_one({"_id": ObjectId(existing['user_id'])})
        conflict_user_name = conflict_user.get('name', existing['user_id']) if conflict_user else existing['user_id']
        
        return jsonify({
            "status": "error",
            "message": "Conflito de horário detectado",
            "conflict": {
                "date": existing['date'],
                "startTime": existing['startTime'],
                "endTime": existing['endTime'],
                "location": existing['location'],
                "description": existing['description'],
                "responsible": existing['responsible'],
                "user": conflict_user_name,
                "email": conflict_user.get('email', '')
            }
        }), 409

    # Create new reservation
    new_reservation = {
        "user_id": current_user,
        "date": data['date'],
        "startTime": data['startTime'],
        "endTime": data['endTime'],
        "location": data['location'],
        "description": data['description'],
        "responsible": data['responsible'],
        "email": data.get('email', ''),
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        result = reservations_collection.insert_one(new_reservation)
        new_reservation['_id'] = str(result.inserted_id)
        return jsonify({
            "status": "success",
            "message": "Reserva criada com sucesso",
            "reservation": new_reservation
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Erro ao criar reserva: " + str(e)
        }), 500

@app.route("/api/reservations/<date>")
@jwt_required()
def get_day_reservations(date):
    try:
        reservations = list(reservations_collection.find({"date": date}))
        
        # Convert ObjectId to string for JSON serialization
        for reservation in reservations:
            reservation['_id'] = str(reservation['_id'])
            
            # Get user details for each reservation
            user = users_collection.find_one({"_id": ObjectId(reservation['user_id'])})
            if user:
                reservation['user_name'] = user.get('name', reservation['user_id'])
                reservation['user_email'] = user.get('email', '')
        
        return jsonify({"reservations": reservations})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Erro ao buscar reservas: " + str(e)
        }), 500

@app.route("/api/reservations/check-conflict", methods=["POST"])
@jwt_required()
def check_reservation_conflict():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    data = request.get_json()
    
    # Check for existing reservations in the same location and time
    existing = reservations_collection.find_one({
        "date": data['date'],
        "location": data['location'],
        "$or": [
            {
                "startTime": {"$lt": data['endTime']},
                "endTime": {"$gt": data['startTime']}
            },
            {
                "startTime": data['startTime'],
                "endTime": data['endTime']
            }
        ]
    })

    if existing:
        # Get the user who created the conflicting reservation
        conflict_user = users_collection.find_one({"_id": ObjectId(existing['user_id'])})
        conflict_user_name = conflict_user.get('name', existing['user_id']) if conflict_user else existing['user_id']
        
        return jsonify({
            "hasConflict": True,
            "conflict": {
                "date": existing['date'],
                "startTime": existing['startTime'],
                "endTime": existing['endTime'],
                "location": existing['location'],
                "description": existing['description'],
                "responsible": existing['responsible'],
                "user": conflict_user_name,
                "email": conflict_user.get('email', '')
            },
            "message": f"Já existe uma reserva para este local das {existing['startTime']} às {existing['endTime']} por {conflict_user_name}"
        })

    return jsonify({"hasConflict": False})

@app.route("/api/reservations/<id>", methods=["PUT"])
@jwt_required()
def update_reservation(id):
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    data = request.get_json()
    current_user = get_jwt_identity()
    
    # Check if reservation exists and belongs to user
    reservation = reservations_collection.find_one({"_id": ObjectId(id)})
    if not reservation:
        return jsonify({"status": "error", "message": "Reserva não encontrada"}), 404
    
    if reservation['user_id'] != current_user:
        return jsonify({"status": "error", "message": "Não autorizado"}), 403

    # Check for conflicts with other reservations
    existing = reservations_collection.find_one({
        "_id": {"$ne": ObjectId(id)},
        "date": data.get('date', reservation['date']),
        "location": data.get('location', reservation['location']),
        "$or": [
            {
                "startTime": {"$lt": data.get('endTime', reservation['endTime'])},
                "endTime": {"$gt": data.get('startTime', reservation['startTime'])}
            },
            {
                "startTime": data.get('startTime', reservation['startTime']),
                "endTime": data.get('endTime', reservation['endTime'])
            }
        ]
    })

    if existing:
        # Get the user who created the conflicting reservation
        conflict_user = users_collection.find_one({"_id": ObjectId(existing['user_id'])})
        conflict_user_name = conflict_user.get('name', existing['user_id']) if conflict_user else existing['user_id']
        
        return jsonify({
            "status": "error",
            "message": f"Conflito de horário com reserva existente de {conflict_user_name}",
            "conflict": {
                "date": existing['date'],
                "startTime": existing['startTime'],
                "endTime": existing['endTime'],
                "location": existing['location'],
                "description": existing['description'],
                "responsible": existing['responsible'],
                "user": conflict_user_name,
                "email": conflict_user.get('email', '')
            }
        }), 409

    # Update reservation
    update_data = {
        "location": data.get('location', reservation['location']),
        "date": data.get('date', reservation['date']),
        "startTime": data.get('startTime', reservation['startTime']),
        "endTime": data.get('endTime', reservation['endTime']),
        "description": data.get('description', reservation['description']),
        "responsible": data.get('responsible', reservation['responsible']),
        "email": data.get('email', reservation['email']),
        "updated_at": datetime.utcnow()
    }

    try:
        reservations_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        return jsonify({"status": "success", "message": "Reserva atualizada com sucesso"})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Erro ao atualizar reserva: " + str(e)
        }), 500

@app.route("/api/reservations/<id>", methods=["DELETE"])
@jwt_required()
def delete_reservation(id):
    current_user = get_jwt_identity()
    
    # Check if reservation exists and belongs to user
    reservation = reservations_collection.find_one({"_id": ObjectId(id)})
    if not reservation:
        return jsonify({"status": "error", "message": "Reserva não encontrada"}), 404
    
    if reservation['user_id'] != current_user:
        return jsonify({"status": "error", "message": "Não autorizado"}), 403

    try:
        reservations_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success", "message": "Reserva cancelada com sucesso"})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Erro ao cancelar reserva: " + str(e)
        }), 500

init_video_routes(app)

if __name__ == "__main__":
    app.run(debug=True, port=5050, host='0.0.0.0')
