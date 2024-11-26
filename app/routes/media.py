from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
import json

bp = Blueprint('media', __name__)

@bp.route('/api/media/search', methods=['POST'])
@jwt_required()
def search_media():
    try:
        print("\n=== Starting Media Search ===")
        
        # Get database connection and verify it
        from app.config.database import get_db
        db = get_db()
        print(f"\nDatabase collections: {db.list_collection_names()}")
        
        services_collection = db['services']
        
        # First, let's see what's in the database
        all_docs = list(services_collection.find())
        print(f"\nTotal documents in collection: {len(all_docs)}")
        print("\nAll documents in collection:")
        for doc in all_docs:
            print(f"\nDocument ID: {doc['_id']}")
            print(f"URL: {doc.get('url', 'No URL')}")
            print(f"Created At: {doc.get('created_at', 'No created_at')}")
            print(f"Title: {doc.get('title', 'No title')}")
            print("---")
        
        data = request.get_json()
        if not data:
            print("Error: Invalid JSON data")
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
            
        url = data.get('url')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        print(f"\nSearch parameters:")
        print(f"URL: {url}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        
        # Build query
        query = {}
        
        # Handle date range query for string dates
        if start_date and end_date:
            # Add time to match the format in MongoDB (YYYY-MM-DD HH:mm:ss)
            start_datetime = f"{start_date} 00:00:00"
            end_datetime = f"{end_date} 23:59:59"
            
            query['created_at'] = {
                '$gte': start_datetime,
                '$lte': end_datetime
            }
            
            print(f"\nDate range query:")
            print(f"Looking for documents between {start_datetime} and {end_datetime}")
            
            # Test the date query separately
            date_results = list(services_collection.find({'created_at': query['created_at']}))
            print(f"\nDocuments matching ONLY date range: {len(date_results)}")
            for doc in date_results:
                print(f"Found document with date: {doc.get('created_at')}")
                print(f"Title: {doc.get('title')}")
                print("---")
        
        if url:
            query['url'] = {'$regex': url, '$options': 'i'}
            # Test URL query separately
            url_results = list(services_collection.find({'url': query['url']}))
            print(f"\nDocuments matching ONLY URL: {len(url_results)}")
            for doc in url_results:
                print(f"Found document with URL: {doc.get('url')}")
                print(f"Title: {doc.get('title')}")
                print("---")
        
        print(f"\nFinal MongoDB query: {json.loads(json_util.dumps(query))}")
        
        if not query:
            print("Error: No search criteria provided")
            return jsonify({
                'status': 'error',
                'message': 'URL or date range is required'
            }), 400
        
        # Execute the final query
        media_posts = list(services_collection.find(
            query,
            {'url': 1, 'media_posts': 1, 'created_at': 1}
        ).sort('created_at', -1))
        
        print(f"\nFound {len(media_posts)} media posts matching criteria")
        
        # Convert ObjectId to string for JSON serialization
        for post in media_posts:
            post['_id'] = str(post['_id'])
        
        print("\n=== Search Results ===")
        print(json.loads(json_util.dumps(media_posts)))
        print("=== Search Completed ===\n")
        
        return jsonify({
            'status': 'success',
            'media_posts': media_posts
        })
    
    except Exception as e:
        print(f"Error in media search: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'Error searching media: {str(e)}'
        }), 500