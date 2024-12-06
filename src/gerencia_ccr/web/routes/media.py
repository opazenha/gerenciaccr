from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
import json

def init_media_routes(app, services_collection):
    media_bp = Blueprint('media', __name__)
    
    @media_bp.route('/api/media/search', methods=['POST'])
    @jwt_required()
    def search_media():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
                
            url = data.get('url')
            start_date = data.get('startDate')
            end_date = data.get('endDate')
            
            # Build query
            query = {}
            
            # Handle date range query
            if start_date and end_date:
                start_str = f"{start_date} 00:00:00"
                end_str = f"{end_date} 23:59:59"
                
                date_query = {
                    'created_at': {
                        '$gte': start_str,
                        '$lte': end_str
                    }
                }
                query.update(date_query)
            
            # Add URL to query if provided
            if url:
                query['url'] = {'$regex': url, '$options': 'i'}
            
            # Execute query
            results = list(services_collection.find(query))
            
            # Convert ObjectId to string for JSON serialization
            json_results = json.loads(json_util.dumps(results))
            
            return jsonify({
                'status': 'success',
                'data': json_results
            })
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    app.register_blueprint(media_bp)
