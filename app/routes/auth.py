from flask import Blueprint, request, jsonify
from app.services.auth_service import login_user, register_user

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route("/login", methods=["POST", "OPTIONS"])
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

    result, status_code = login_user(email, password)
    return jsonify(result), status_code

@bp.route("/register", methods=["POST", "OPTIONS"])
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

    result, status_code = register_user(email, password, name)
    return jsonify(result), status_code
