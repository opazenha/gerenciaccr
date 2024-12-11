from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
import json
import os
import time
from gerencia_ccr.crews.request_flow import ProcessRequestFlow
from gerencia_ccr.web.services.email_service import send_markdown_email

def init_media_routes(app, services_collection):
    media_bp = Blueprint('media', __name__)
    
    @media_bp.route('/api/media/create_posts', methods=['POST'])
    @jwt_required()
    def create_posts():
        try:
            data = request.get_json()
            if not data or 'request' not in data:
                return jsonify({'status': 'error', 'message': 'Missing request content'}), 400
                
            user_input = data['request']
            
            # Create and run the flow
            flow = ProcessRequestFlow(request=user_input)
            flow.kickoff()
            
            # Retrieve generated posts
            posts = []
            # Get the project root directory (4 levels up from routes/media.py)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            posts_dir = os.path.join(project_root, 'posts')
            print(f"\n[DEBUG] Posts directory path: {posts_dir}")
            
            if not os.path.exists(posts_dir):
                print(f"[DEBUG] Posts directory does not exist, creating it now")
                os.makedirs(posts_dir)  # Create the directory if it doesn't exist
                return jsonify({
                    'status': 'warning',
                    'message': 'No posts available yet',
                    'posts': []
                })
            
            print(f"[DEBUG] Reading files from posts directory")
            for filename in os.listdir(posts_dir):
                if filename.endswith(".md"):
                    print(f"\n[DEBUG] Processing file: {filename}")
                    try:
                        with open(os.path.join(posts_dir, filename), 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                            print(f"[DEBUG] Successfully read markdown from {filename}")
                            posts.append(markdown_content)
                            print(f"[DEBUG] Successfully added post to list")
                    except Exception as e:
                        print(f"[ERROR] Error reading {filename}: {str(e)}")
                        continue
            
            print(f"\n[DEBUG] Total posts processed: {len(posts)}")
            
            # Cleanup: Delete all markdown files after reading
            print("[DEBUG] Starting cleanup of markdown files")
            for filename in os.listdir(posts_dir):
                if filename.endswith(".md"):
                    try:
                        file_path = os.path.join(posts_dir, filename)
                        os.remove(file_path)
                        print(f"[DEBUG] Successfully deleted {filename}")
                    except Exception as e:
                        print(f"[ERROR] Error deleting {filename}: {str(e)}")
                        continue
            
            if not posts:
                print("[DEBUG] No posts found, returning warning")
                return jsonify({
                    'status': 'warning',
                    'message': 'No posts were generated',
                    'posts': []
                })
            
            print("[DEBUG] Successfully returning posts")
            
            # Send email with markdown content
            try:
                # Join all posts with a separator
                combined_markdown = "\n\n---\n\n".join(posts)
                email_sent = send_markdown_email(
                    "ccrbraga.midiacomunicacao@gmail.com",
                    combined_markdown,
                    "Novos Posts Gerados"
                )
                
                time.sleep(1)
                
                email_sent = send_markdown_email(
                    "lucaszenh@gmail.com",
                    combined_markdown,
                    "Novos Posts Gerados"
                )
                if email_sent:
                    print("[DEBUG] Successfully sent email with markdown content")
                else:
                    print("[WARNING] Failed to send email with markdown content")
            except Exception as email_error:
                print(f"[ERROR] Error sending email: {str(email_error)}")
                # Continue with the response even if email fails
            
            return jsonify({
                'status': 'success',
                'message': 'Posts generated successfully',
                'posts': posts
            })
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
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
