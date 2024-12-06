from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId

def init_reservation_routes(app, mongo_client):
    @app.route('/api/reservations', methods=['POST'])
    @jwt_required()
    def create_reservation():
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['date', 'start_time', 'end_time', 'title']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Check for conflicts
        conflicts = mongo_client.db.reservations.find({
            'date': data['date'],
            'title': data['title'],  # Same room
            '$or': [
                {
                    'start_time': {'$lt': data['end_time']},
                    'end_time': {'$gt': data['start_time']}
                },
                {
                    'start_time': {'$gte': data['start_time']},
                    'end_time': {'$lte': data['end_time']}
                }
            ]
        })
        
        conflicts_list = list(conflicts)
        if conflicts_list:
            return jsonify({
                'status': 'error',
                'message': 'Conflito de horário: Este espaço já está reservado para este horário',
                'conflicts': [{
                    'id': str(r['_id']),
                    'user_id': str(r['user_id']),
                    'date': r['date'],
                    'start_time': r['start_time'],
                    'end_time': r['end_time'],
                    'title': r['title'],
                    'description': r.get('description', '')
                } for r in conflicts_list]
            }), 409
        
        reservation = {
            'user_id': ObjectId(user_id),
            'date': data['date'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'title': data['title'],
            'description': data.get('description', ''),
            'created_at': datetime.utcnow()
        }
        
        result = mongo_client.db.reservations.insert_one(reservation)
        return jsonify({
            'status': 'success',
            'message': 'Reserva criada com sucesso',
            'id': str(result.inserted_id)
        }), 201

    @app.route('/api/reservations/day/<date>')
    @jwt_required()
    def get_day_reservations(date):
        reservations = mongo_client.db.reservations.find({'date': date})
        return jsonify([{
            'id': str(r['_id']),
            'user_id': str(r['user_id']),
            'date': r['date'],
            'start_time': r['start_time'],
            'end_time': r['end_time'],
            'title': r['title'],
            'description': r.get('description', '')
        } for r in reservations])

    @app.route('/api/reservations/check-conflict', methods=['POST'])
    @jwt_required()
    def check_reservation_conflict():
        data = request.get_json()
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']
        
        conflicts = mongo_client.db.reservations.find({
            'date': date,
            '$or': [
                {
                    'start_time': {'$lt': end_time},
                    'end_time': {'$gt': start_time}
                },
                {
                    'start_time': {'$gte': start_time},
                    'end_time': {'$lte': end_time}
                }
            ]
        })
        
        return jsonify([{
            'id': str(r['_id']),
            'user_id': str(r['user_id']),
            'date': r['date'],
            'start_time': r['start_time'],
            'end_time': r['end_time'],
            'title': r['title']
        } for r in conflicts])

    @app.route('/api/reservations/range')
    @jwt_required()
    def get_reservations_range():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({
                'status': 'error',
                'message': 'start_date and end_date are required'
            }), 400
            
        reservations = mongo_client.db.reservations.find({
            'date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('date', 1)
        
        return jsonify({
            'status': 'success',
            'reservations': [{
                'id': str(r['_id']),
                'user_id': str(r['user_id']),
                'date': r['date'],
                'start_time': r['start_time'],
                'end_time': r['end_time'],
                'title': r['title'],
                'description': r.get('description', '')
            } for r in reservations]
        })

    @app.route('/api/reservations/<id>', methods=['PUT'])
    @jwt_required()
    def update_reservation(id):
        user_id = get_jwt_identity()
        data = request.get_json()
        
        reservation = mongo_client.db.reservations.find_one({
            '_id': ObjectId(id),
            'user_id': ObjectId(user_id)
        })
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
            
        update_data = {
            'date': data['date'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'title': data['title'],
            'description': data.get('description', ''),
            'updated_at': datetime.utcnow()
        }
        
        mongo_client.db.reservations.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_data}
        )
        
        return jsonify({'message': 'Reservation updated successfully'})

    @app.route('/api/reservations/<id>', methods=['DELETE'])
    @jwt_required()
    def delete_reservation(id):
        user_id = get_jwt_identity()
        result = mongo_client.db.reservations.delete_one({
            '_id': ObjectId(id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Reservation not found'}), 404
            
        return jsonify({'message': 'Reservation deleted successfully'})
