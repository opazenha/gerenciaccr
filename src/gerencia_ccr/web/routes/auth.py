from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import bcrypt

def init_auth_routes(app, mongo_db):
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        print(f"Login attempt for email: {email}")
        print(f"Database collections: {mongo_db.list_collection_names()}")
        
        user = mongo_db.users.find_one({'email': email})
        print(f"Query result: {user}")
        
        if not user:
            print(f"User not found with email: {email}")
            return jsonify({'message': 'Email ou senha inválidos'}), 401

        try:
            password_matches = bcrypt.checkpw(password.encode('utf-8'), user['password'])
            print(f"Password check result: {password_matches}")
            if not password_matches:
                return jsonify({'message': 'Email ou senha inválidos'}), 401
        except Exception as e:
            print(f"Error checking password: {str(e)}")
            return jsonify({'message': 'Erro ao verificar senha'}), 500

        access_token = create_access_token(
            identity=str(user['_id']),
            expires_delta=timedelta(days=1)
        )
        return jsonify({'token': access_token}), 200

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return jsonify({'message': 'Todos os campos são obrigatórios'}), 400

        if mongo_db.users.find_one({'email': email}):
            return jsonify({'message': 'Email já cadastrado'}), 400

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            'email': email,
            'password': hashed,
            'name': name,
            'created_at': datetime.utcnow()
        }
        
        result = mongo_db.users.insert_one(user)
        access_token = create_access_token(
            identity=str(result.inserted_id),
            expires_delta=timedelta(days=1)
        )
        return jsonify({'token': access_token}), 201
