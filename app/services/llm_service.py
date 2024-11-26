import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
flash_model = genai.GenerativeModel('gemini-flash')
pro_model = genai.GenerativeModel('gemini-pro')

# Rate limiting for Gemini Pro
last_pro_request_time = 0

def make_rate_limited_request(prompt, is_flash=False):
    global last_pro_request_time
    
    if not is_flash:
        # Check if we need to wait
        current_time = time.time()
        time_since_last_request = current_time - last_pro_request_time
        
        if time_since_last_request < 30:  # Ensure 30 seconds between pro requests
            wait_time = 30 - time_since_last_request
            print(f"Rate limiting: waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        
        last_pro_request_time = time.time()
        model = pro_model
    else:
        model = flash_model
    
    response = model.generate_content(prompt)
    return response.text

def process_sermon(transcription):
    print("Processing sermon in chunks with Gemini Flash...")
    chunks = [transcription[i:i+4000] for i in range(0, len(transcription), 4000)]
    summary_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {i}/{len(chunks)}...")
        prompt = '''You are amazing on summarizing sermons. You take note of ALL the biblie references mentioned on the text and list them at the end of the summary. ALWAYS respond in Portuguese.
        Just output the summary itself, do not say things like Here is the Summary, or give it a title. Do not add extra lines between topics.
        You will be provided parts of the sermon, do not speculate on previous parts, focus on working with the content provided at a time.
        DO NOT use markdown on response, use pure text. According to the part of the sermon provided by the speaker, summarize the following text: {chunk}'''
        
        summary = make_rate_limited_request(prompt.format(chunk=chunk), is_flash=True)
        summary_parts.append(summary)
    
    return "\n\n".join(summary_parts)

def generate_summary(transcript):
    print("Generating final summary with Gemini Pro...")
    prompt = '''You are amazing on summarizing sermons. You take note of ALL the biblie references mentioned on the text and list them at the end of the summary. ALWAYS respond in Portuguese.
        Just output the summary itself, do not say things like Here is the Summary, or give it a title. Do not add extra lines between topics.
        You will be provided parts of the sermon, do not speculate on previous parts, focus on working with the content provided at a time.
        DO NOT use markdown on response, use pure text. According to the part of the sermon provided by the speaker, summarize the following text: {text}'''
    
    return make_rate_limited_request(prompt.format(text=transcript))

def generate_media_posts(transcript):
    print("Generating social media posts with Gemini Pro...")
    prompt = '''You are amazing on creating social media content. You work for a church media team for years now.
   Your job is to take the sermon text and create a social media posts. The focus is Instagram posts and Stories.
   The idea is to make the congregation engaged during the week and keep them thinking about the past sermon during the week.
   You are responsible for 3 posts, 1 for Monday, 1 for Wednesday and 1 for Friday. The posts should be short and to the point but engaging. Try to include a call for action.
   You will provide the text for the posts as well as image ideas. Try to provide the image ideas in a prompt like format so that it can be used a have good results on another AI for image generation.
   For each of the posts you will provide 2 versions of each for more flexibility to choose from. ALWAYS respond in Portuguese.
   The content to be considered is partial summary from chuncks of the sermon, and a final summary at the end. Navigate the content and do the tasks accordingly.
   DO NOT use markdown on response, use pure text. Content: {text}'''
    
    content = make_rate_limited_request(prompt.format(text=transcript))
    posts = [post.strip() for post in content.split('\n\n') if post.strip()]
    return [{'text': post} for post in posts]

def generate_kids_report(transcript):
    print("Generating kids report with Gemini Pro...")
    prompt = '''You are amazing on developing on sermons. You are to generate a simple guided sermon to be handled by the kids team leader to be presented to the kids next week.
    Elaborate the content in a consise way holding 3 main topics, each with its own elaboration with easy to digest information since this is for kids learning.
    According to the content provided, generate a prompt to be used with DALLE3 to generate an image with only outlines and no colour so the kids can paint during class.
    The prompt must be provided as: <prompt> Prompt text here...
    ALWAYS respond in Portuguese. DO NOT use markdown on response, use pure text. Use the following text: {text}'''
    
    return make_rate_limited_request(prompt.format(text=transcript))

def generate_gc_report(transcript):
    print("Generating small group report with Gemini Pro...")
    prompt = '''You are amazing on developing on sermons. You are to generate a simple guided sermon to be handled by the small group team leader to be presented to the groups during the week.
    Elaborate the content in a consise way holding 3 main topics, each with its own elaboration with easy to digest information for quick learning.
    ALWAYS respond in Portuguese. DO NOT use markdown on response, use pure text. Use the following text: {text}'''
    
    return make_rate_limited_request(prompt.format(text=transcript))