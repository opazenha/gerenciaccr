from flask import request, jsonify
from flask_jwt_extended import jwt_required
import os
import yt_dlp
import whisper
from datetime import datetime
from ...services.llm_service import (
    process_sermon,
    generate_summary,
    generate_media_posts,
    generate_kids_report,
    generate_gc_report
)

def init_process_routes(video_bp, services_collection):
    @video_bp.route('/api/video/process', methods=['POST'])
    @jwt_required()
    def process_video():
        try:
            print("\n=== Starting Video Processing ===")
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
                
            url = data.get('url')
            option = data.get('option')

            if not url:
                return jsonify({'status': 'error', 'message': 'URL is required'}), 400

            try:
                print("Step 1/4: Downloading video...")
                # Configure yt-dlp
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': 'downloads/%(id)s.%(ext)s',
                }

                # Download video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_id = info['id']
                    audio_path = f"downloads/{video_id}.mp3"

                print("Step 2/4: Loading Whisper model...")
                # Load Whisper model
                model = whisper.load_model("large-v3")

                print("Step 3/4: Transcribing audio...")
                # Transcribe audio
                result = model.transcribe(audio_path)
                transcription = result["text"]

                # Clean up audio file
                os.remove(audio_path)

                print("Step 4/4: Processing content...")
                # Process sermon in chunks
                partial_summary = process_sermon(transcription)
                
                # Generate final summary
                final_summary = generate_summary(partial_summary)
                
                # Initialize optional reports
                media_posts = None
                kids_report = None
                gc_report = None
                
                # Generate additional reports based on option
                if option in ['media', 'completo']:
                    media_posts = generate_media_posts(final_summary)
                
                if option == 'completo':
                    kids_report = generate_kids_report(final_summary)
                    gc_report = generate_gc_report(final_summary)

                # Save to database
                service_data = {
                    'url': url,
                    'transcription': transcription,
                    'partial_summary': partial_summary,
                    'final_summary': final_summary,
                    'media_posts': media_posts,
                    'kids_report': kids_report,
                    'gc_report': gc_report,
                    'created_at': datetime.utcnow()
                }
                
                result = services_collection.insert_one(service_data)
                service_id = str(result.inserted_id)
                
                # Prepare response
                response = {
                    'status': 'success',
                    'message': 'Service processed successfully',
                    'service_id': service_id,
                    'final_summary': final_summary,
                }
                
                if option in ['media', 'completo']:
                    response['media_posts'] = media_posts
                
                if option == 'completo':
                    response['kids_report'] = kids_report
                    response['gc_report'] = gc_report
                
                return jsonify(response)

            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Error generating content: {str(e)}'
                }), 500
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error processing video: {str(e)}'
            }), 500