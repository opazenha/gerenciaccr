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

def download_and_trim_video(url):
    """Download video and trim the first 40 minutes"""
    print("Step 1/4: Downloading video...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'progress': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        audio_path = f"downloads/{video_id}.mp3"

    # Trim the first 40 minutes of the audio file
    print("Step 1.5/4: Trimming audio file...")
    start_time = "00:40:00"
    trimmed_audio_path = f"downloads/{video_id}_trimmed.mp3"
    command = f"ffmpeg -i {audio_path} -ss {start_time} -c copy {trimmed_audio_path}"
    subprocess.call(command, shell=True)
    
    # Clean up original audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return trimmed_audio_path

def transcribe_video(audio_path):
    """Transcribe the video audio using Whisper"""
    print("Step 2/4: Transcribing video...")
    model = whisper.load_model("medium")

    result = model.transcribe(
        audio_path,
        language="pt",
        task="transcribe",
        verbose=True,
        initial_prompt="Este é um sermão em português."
    )
    
    # Clean up audio files
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    # Clean up any partial downloads
    for f in os.listdir('downloads'):
        if f.endswith('.part') or f.endswith('.ytdl'):
            os.remove(os.path.join('downloads', f))
            
    return result["text"]

def transcribe_video_groq(audio_path):
    """Transcribe the video audio using Groq's Whisper API with file size handling"""
    from groq import Groq
    import os
    from pydub import AudioSegment
    import tempfile

    MAX_SIZE_MB = 24
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    
    client = Groq()
    all_transcriptions = []

    try:
        if file_size_mb <= MAX_SIZE_MB:
            # Process the whole file
            with open(audio_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-large-v3",
                    prompt="É um sermão em Português.",
                    response_format="json",
                    language="pt",
                    temperature=0.0
                )
                return transcription.text
        else:
            # Split and process file in chunks
            audio = AudioSegment.from_mp3(audio_path)
            chunk_length_ms = 20 * 60 * 1000  # 20 minutes chunks
            
            # Create a directory for chunks if it doesn't exist
            chunks_dir = "downloads/chunks"
            os.makedirs(chunks_dir, exist_ok=True)
            
            # Split audio into chunks and save them
            chunks = [audio[i:i + chunk_length_ms] 
                     for i in range(0, len(audio), chunk_length_ms)]
            
            for i, chunk in enumerate(chunks):
                chunk_path = os.path.join(chunks_dir, f"chunk_{i}.mp3")
                print(f"Saving chunk {i} to {chunk_path}")
                chunk.export(chunk_path, format="mp3")
                
                with open(chunk_path, "rb") as file:
                    print(f"Processing chunk {i}")
                    transcription = client.audio.transcriptions.create(
                        file=file,
                        model="whisper-large-v3",
                        prompt="É um sermão em Português.",
                        response_format="json",
                        language="pt",
                        temperature=0.0
                    )
                    all_transcriptions.append(transcription.text)
                
                # Clean up the chunk file
                os.remove(chunk_path)
            
            # Clean up chunks directory if empty
            try:
                os.rmdir(chunks_dir)
            except:
                pass
                
            return " ".join(all_transcriptions)
            
    except Exception as e:
        print(f"Error in Groq transcription: {str(e)}")
        raise


def process_content(transcription, option):
    """Process the transcribed content based on the selected option"""
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
        
    return {
        'partial_summary': partial_summary,
        'final_summary': final_summary,
        'media_posts': media_posts,
        'kids_report': kids_report,
        'gc_report': gc_report
    }

def save_to_database(services_collection, url, video_title, transcription, processed_content):
    """Save all processed content to the database"""
    service_data = {
        'url': url,
        'title': video_title,
        'transcription': transcription,
        'partial_summary': processed_content['partial_summary'],
        'final_summary': processed_content['final_summary'],
        'media_posts': processed_content['media_posts'],
        'kids_report': processed_content['kids_report'],
        'gc_report': processed_content['gc_report'],
        'created_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    result = services_collection.insert_one(service_data)
    return str(result.inserted_id)

def process_video_task(url, user, video_title, services_collection, option):
    """Background task to process the video"""
    try:
        # Step 1: Download and trim video
        audio_path = download_and_trim_video(url)
        
        # Step 2: Transcribe video
        transcription = transcribe_video_groq(audio_path)
        
        # Step 3: Process content
        processed_content = process_content(transcription, option)
        
        # Step 4: Save to database
        service_id = save_to_database(services_collection, url, video_title, 
                                    transcription, processed_content)

        # Send email notification
        send_completion_email(user['email'], url)
        
    except Exception as e:
        print(f"Error in video processing task: {str(e)}")