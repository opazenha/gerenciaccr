import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize both models
flash_model = genai.GenerativeModel('gemini-1.5-flash')
pro_model = genai.GenerativeModel('gemini-1.5-pro')

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
            print(f"[Rate Limit] Aguardando {wait_time:.2f} segundos para próxima requisição...")
            time.sleep(wait_time)
        
        print("[LLM] Usando modelo Gemini 1.5 Pro")
        last_pro_request_time = time.time()
        model = pro_model
    else:
        print("[LLM] Usando modelo Gemini 1.5 Flash")
        model = flash_model
    
    print("[LLM] Enviando requisição...")
    try:
        response = model.generate_content(prompt)
        print("[LLM] Resposta recebida com sucesso")
        return response.text
    except Exception as e:
        print(f"[LLM] Erro na requisição: {str(e)}")
        raise e

def process_sermon(transcription):
    print("\n=== Iniciando Processamento do Sermão ===")
    print(f"[Sermon] Tamanho da transcrição: {len(transcription)} caracteres")
    chunks = [transcription[i:i+4000] for i in range(0, len(transcription), 4000)]
    print(f"[Sermon] Dividido em {len(chunks)} partes para processamento")
    summary_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Sermon] Processando parte {i}/{len(chunks)}...")
        print(f"[Sermon] Tamanho da parte: {len(chunk)} caracteres")
        prompt = '''You are amazing on summarizing sermons. You take note of ALL the biblie references mentioned on the text and list them at the end of the summary. ALWAYS respond in Portuguese.
        Just output the summary itself, do not say things like Here is the Summary, or give it a title. Do not add extra lines between topics.
        You will be provided parts of the sermon, do not speculate on previous parts, focus on working with the content provided at a time.
        DO NOT use markdown on response, use pure text. According to the part of the sermon provided by the speaker, summarize the following text: {chunk}'''
        
        summary = make_rate_limited_request(prompt.format(chunk=chunk), is_flash=True)
        print(f"[Sermon] Parte {i} processada com sucesso")
        summary_parts.append(summary)
    
    print("[Sermon] Todas as partes processadas com sucesso")
    return "\n\n".join(summary_parts)

def generate_summary(transcript):
    print("\n=== Gerando Resumo Final ===")
    print(f"[Summary] Tamanho do texto: {len(transcript)} caracteres")
    prompt = '''You are amazing on summarizing sermons. You take note of ALL the biblie references mentioned on the text and list them at the end of the summary. ALWAYS respond in Portuguese.
        Just output the summary itself, do not say things like Here is the Summary, or give it a title. Do not add extra lines between topics.
        You will be provided parts of the sermon, do not speculate on previous parts, focus on working with the content provided at a time.
        DO NOT use markdown on response, use pure text. According to the part of the sermon provided by the speaker, summarize the following text: {text}'''
    
    print("[Summary] Enviando para processamento...")
    result = make_rate_limited_request(prompt.format(text=transcript))
    print("[Summary] Resumo final gerado com sucesso")
    return result

def generate_media_posts(transcript):
    print("\n=== Gerando Posts para Redes Sociais ===")
    print(f"[Media] Tamanho do texto: {len(transcript)} caracteres")
    prompt = '''You are amazing on creating social media content. You work for a church media team for years now.
   Your job is to take the sermon text and create a social media posts. The focus is Instagram posts and Stories.
   The idea is to make the congregation engaged during the week and keep them thinking about the past sermon during the week.
   You are responsible for 3 posts, 1 for Monday, 1 for Wednesday and 1 for Friday. The posts should be short and to the point but engaging. Try to include a call for action.
   You will provide the text for the posts as well as image ideas. Try to provide the image ideas in a prompt like format so that it can be used a have good results on another AI for image generation.
   For each of the posts you will provide 2 versions of each for more flexibility to choose from. ALWAYS respond in Portuguese.
   The content to be considered is partial summary from chuncks of the sermon, and a final summary at the end. Navigate the content and do the tasks accordingly.
   DO NOT use markdown on response, use pure text. Content: {text}'''
    
    print("[Media] Gerando conteúdo para posts...")
    content = make_rate_limited_request(prompt.format(text=transcript))
    posts = [post.strip() for post in content.split('\n\n') if post.strip()]
    print(f"[Media] {len(posts)} posts gerados com sucesso")
    return [{'text': post} for post in posts]

def generate_kids_report(transcript):
    print("\n=== Gerando Relatório para Crianças ===")
    print(f"[Kids] Tamanho do texto: {len(transcript)} caracteres")
    prompt = '''You are amazing on developing on sermons. You are to generate a simple guided sermon to be handled by the kids team leader to be presented to the kids next week.
    Elaborate the content in a consise way holding 3 main topics, each with its own elaboration with easy to digest information since this is for kids learning.
    According to the content provided, generate a prompt to be used with DALLE3 to generate an image with only outlines and no colour so the kids can paint during class.
    The prompt must be provided as: <prompt> Prompt text here...
    ALWAYS respond in Portuguese. DO NOT use markdown on response, use pure text. Use the following text: {text}'''
    
    print("[Kids] Gerando conteúdo...")
    result = make_rate_limited_request(prompt.format(text=transcript))
    print("[Kids] Relatório gerado com sucesso")
    return result

def generate_gc_report(transcript):
    print("\n=== Gerando Relatório para Grupos ===")
    print(f"[GC] Tamanho do texto: {len(transcript)} caracteres")
    prompt = '''You are amazing on developing on sermons. You are to generate a simple guided sermon to be handled by the small group team leader to be presented to the groups during the week.
    Elaborate the content in a consise way holding 3 main topics, each with its own elaboration with easy to digest information for quick learning.
    ALWAYS respond in Portuguese. DO NOT use markdown on response, use pure text. Use the following text: {text}'''
    
    print("[GC] Gerando conteúdo...")
    result = make_rate_limited_request(prompt.format(text=transcript))
    print("[GC] Relatório gerado com sucesso")
    return result