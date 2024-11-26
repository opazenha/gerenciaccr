from flask import current_app
from flask_jwt_extended import create_access_token
import bcrypt
from datetime import datetime

def login_user(email, password):
    users_collection = current_app.config['users_collection']
    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return {
            "status": "success",
            "token": access_token,
            "user": {
                "email": user["email"],
                "name": user["name"]
            }
        }, 200
    return {"status": "error", "message": "Credenciais inválidas"}, 401

def register_user(email, password, name):
    users_collection = current_app.config['users_collection']
    if users_collection.find_one({"email": email}):
        return {"status": "error", "message": "Email já cadastrado"}, 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "email": email,
        "password": hashed,
        "name": name,
        "created_at": datetime.utcnow()
    }
    
    users_collection.insert_one(user)
    return {"status": "success", "message": "Usuário registrado com sucesso"}, 201
