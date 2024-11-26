from flask import request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
import json

def init_search_routes(video_bp, services_collection):
    @video_bp.route('/api/sermons/search', methods=['POST'])
    @jwt_required()
    def search_sermons():
        try:
            print("\n=== Starting Sermon Search ===")
            
            # First, let's see what's in the database
            all_docs = list(services_collection.find())
            print("\nAll documents in collection:")
            for doc in all_docs:
                print(f"Document ID: {doc['_id']}")
                print(f"URL: {doc.get('url')}")
                print(f"Created At: {doc.get('created_at')}")
                print("---")
            
            data = request.get_json()
            if not data:
                print("Error: Invalid JSON data")
                return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
                
            url = data.get('url')
            start_date = data.get('startDate')
            end_date = data.get('endDate')
            
            print(f"Search parameters - URL: {url}, Start Date: {start_date}, End Date: {end_date}")
            
            # Build query
            query = {}
            
            # Handle date range query for string dates
            if start_date and end_date:
                # Convert to the same string format as stored in MongoDB
                start_str = f"{start_date} 00:00:00"
                end_str = f"{end_date} 23:59:59"
                
                print(f"Looking for documents between {start_str} and {end_str}")
                
                # String comparison query
                date_query = {
                    'created_at': {
                        '$gte': start_str,
                        '$lte': end_str
                    }
                }
                
                # Test the date query separately
                date_results = list(services_collection.find(date_query))
                print(f"\nDocuments matching date range:")
                for doc in date_results:
                    print(f"Found document with date: {doc.get('created_at')}")
                
                query.update(date_query)
            
            if url:
                query['url'] = {'$regex': url, '$options': 'i'}
            
            print(f"Final MongoDB query: {json.loads(json_util.dumps(query))}")
            
            if not query:
                print("Error: No search criteria provided")
                return jsonify({
                    'status': 'error',
                    'message': 'URL or date range is required'
                }), 400
            
            # Execute the final query
            sermons = list(services_collection.find(
                query,
                {'url': 1, 'title': 1, 'created_at': 1, 'final_summary': 1}
            ).sort('created_at', -1))
            
            print(f"\nFound {len(sermons)} sermons matching criteria")
            
            # No need to convert dates since they're already strings
            for sermon in sermons:
                sermon['_id'] = str(sermon['_id'])
            
            print("=== Search Results ===")
            print(json.loads(json_util.dumps(sermons)))
            print("=== Search Completed ===\n")
            
            return jsonify({
                'status': 'success',
                'sermons': sermons
            })
        
        except Exception as e:
            print(f"Error in sermon search: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'status': 'error',
                'message': f'Error searching sermons: {str(e)}'
            }), 500