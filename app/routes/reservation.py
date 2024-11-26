from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.reservation_service import (
    create_new_reservation, 
    get_user_reservations, 
    update_reservation_by_id, 
    delete_reservation_by_id,
    get_all_reservations,
    get_date_range_reservations
)

bp = Blueprint('reservation', __name__, url_prefix='/api/reservations')

@bp.route("/", methods=["POST"])
@jwt_required()
def create():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    user_id = get_jwt_identity()
    data = request.get_json()
    
    result, status_code = create_new_reservation(data, user_id)
    return jsonify(result), status_code

@bp.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    result, status_code = get_user_reservations(user_id)
    return jsonify(result), status_code

@bp.route("/all", methods=["GET"])
@jwt_required()
def get_all():
    result, status_code = get_all_reservations()
    return jsonify(result), status_code

@bp.route("/range", methods=["GET"])
@jwt_required()
def get_range():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    print(f"[ROUTE] Received date range request: start={start_date}, end={end_date}")
    
    if not start_date or not end_date:
        return jsonify({"status": "error", "message": "start_date and end_date are required"}), 400
    
    result, status_code = get_date_range_reservations(start_date, end_date)
    print(f"[ROUTE] Returning result: {result}")
    return jsonify(result), status_code

@bp.route("/<reservation_id>", methods=["PUT"])
@jwt_required()
def update(reservation_id):
    if not request.is_json:
        return jsonify({"status": "error", "message": "Missing JSON in request"}), 400

    user_id = get_jwt_identity()
    data = request.get_json()
    
    result, status_code = update_reservation_by_id(reservation_id, data)
    return jsonify(result), status_code

@bp.route("/<reservation_id>", methods=["DELETE"])
@jwt_required()
def delete(reservation_id):
    user_id = get_jwt_identity()
    result, status_code = delete_reservation_by_id(reservation_id)
    return jsonify(result), status_code
