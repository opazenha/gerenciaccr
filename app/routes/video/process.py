from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import yt_dlp
import whisper
import subprocess
from datetime import datetime
from ...services.llm_service import (
    process_sermon,
    generate_summary,
    generate_media_posts,
    generate_kids_report,
    generate_gc_report
)
from ...services.email_service import send_completion_email
from ...models.user import UserModel
from threading import Thread

def init_process_routes(video_bp, services_collection):
    @video_bp.route('/api/video/process', methods=['POST'])
    @jwt_required()
    def process_video():
        try:
            current_user_id = get_jwt_identity()
            user_model = UserModel()
            user = user_model.get_user_by_id(current_user_id)
            if not user or not user.get('email'):
                return jsonify({'status': 'error', 'message': 'User email not found'}), 400

            print("\n=== Starting Video Processing ===")
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
                
            url = data.get('url')
            option = data.get('option')

            if not url:
                return jsonify({'status': 'error', 'message': 'URL is required'}), 400

            # Check if video has already been processed
            existing_video = services_collection.find_one({'url': url})
            if existing_video:
                print(f"Video {url} has already been processed. Using existing document.")
                # Convert ObjectId to string for JSON serialization
                existing_video['_id'] = str(existing_video['_id'])
                
                response = {
                    'status': 'success',
                    'message': 'Vídeo já processado anteriormente. Use outra opção para visualização.',
                }
                
                return jsonify(response)

            # Get video info first
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    video_info = ydl.extract_info(url, download=False)
                    video_title = video_info.get('title', 'Untitled')
                    
                # Start processing in background thread
                thread = Thread(target=process_video_task, args=(url, user, video_title, services_collection, option))
                thread.start()
                
                return jsonify({
                    'status': 'success',
                    'message': f'O vídeo "{video_title}" está a ser processado. Assim que completo enviaremos um email para {user["email"]}. Obrigado!'
                }), 202

            except Exception as e:
                print(f"Error getting video info: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': 'Erro ao obter informações do vídeo. Por favor, verifique a URL.'
                }), 400

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error processing video: {str(e)}'
            }), 500

def process_video_task(url, user, video_title, services_collection, option):
    """Background task to process the video"""
    try:
        # Download video
        print("Step 1/4: Downloading video...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(id)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            audio_path = f"downloads/{video_id}.mp3"

        # Trim the first 40 minutes of the audio file
        print("Step 1.5/4: Trimming audio file...")
        start_time = "00:40:00"
        trimmed_audio_path = f"downloads/{video_id}_trimmed.mp3"
        # Using -t for duration instead of -to for end time
        command = f"ffmpeg -i {audio_path} -ss {start_time} -c copy {trimmed_audio_path}"
        subprocess.call(command, shell=True)
        audio_path = trimmed_audio_path

        # Transcribe video
        print("Step 2/4: Transcribing video...")
        model = whisper.load_model("tiny")

        result = model.transcribe(
            audio_path,
            language="pt",
            task="transcribe",
            verbose=True,
            initial_prompt="Este é um sermão em português."
        )
        transcription = result["text"]

        # Clean up audio files
        os.remove(audio_path)
        if os.path.exists(f"downloads/{video_id}.mp3"):
            os.remove(f"downloads/{video_id}.mp3")

        # Process content
        print("Step 3/4: Processing content...")
        partial_summary = process_sermon(transcription)
        final_summary = generate_summary(partial_summary)
        media_posts = None
        kids_report = None
        gc_report = None

        if option in ['media', 'completo']:
            media_posts = generate_media_posts(final_summary)
        
        if option == 'completo':
            kids_report = generate_kids_report(final_summary)
            gc_report = generate_gc_report(final_summary)

        # Save to database
        service_data = {
            'url': url,
            'title': video_title,  # Add video title to database
            'transcription': transcription,
            'partial_summary': partial_summary,
            'final_summary': final_summary,
            'media_posts': media_posts,
            'kids_report': kids_report,
            'gc_report': gc_report,
            'created_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        result = services_collection.insert_one(service_data)
        service_id = str(result.inserted_id)

        # Send email notification
        send_completion_email(user['email'], url)
        
    except Exception as e:
        print(f"Error in video processing task: {str(e)}")