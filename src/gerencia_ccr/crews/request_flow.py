from crewai.flow.flow import Flow, listen, start, or_
from dotenv import load_dotenv
from litellm import completion
import json

load_dotenv()

class ProcessRequestFlow(Flow):
    model = "gpt-4o-mini"

    def __init__(self, request: str = None):
        super().__init__()
        self.request = request

    def categorize_pro(self, request: str = None):
        print("Triggered 'categorize_pro'")
        request_text = request or self.request

        response = completion(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that takes a client input for social media posts and categorizes it. Return a JSON file WITHOUT QUOTES and json word on it, with the following structure: {\"category\": \"<sermon_or_post-idea_or_bible-verse>\", \"sub_category\": \"<sub_category>\", \"require_development\": <true_or_false>, \"bible_verse\": <verse_or_empty-string>}.",
                },
                {
                    "role": "user",
                    "content": request_text,
                },
            ],
        )

        category = response["choices"][0]["message"]["content"]
        print(f"Category: {category}")

        return category

    def develop_idea(self, request: str = None):
        print("Triggered 'develop_idea'")
        request_text = request or self.request

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant with great knowledge of biblical content. Develop a social media post concept based on {request_text}""",
                },
            ],
        )

        response_develop = response["choices"][0]["message"]["content"]
        print(f"Response develop: {response_develop}")

        return response_develop

    def extract_bible_verse(self, content):
        print("Triggered 'extract_bible_verse'")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant with great knowledge of biblical content. Provide a biblical verse based on {content}""",
                },
            ],
        )

        response_verse = response["choices"][0]["message"]["content"]
        print(f"Response verse: {response_verse}")

        return response_verse

    def generate_post(self, content, sub_category, bible_verse):
        print("Triggered 'generate_post'")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful assistant with great knowledge of biblical content and social media management. Generate a social media post based on the 
                    theme: {sub_category}, 
                    the content: {content} and 
                    the biblical verse: {bible_verse}.
                    Make is short and to the point but engaging. Try to include a call for action.
                    Always respond in Portuguese (PT-PT). 
                    DO NOT use markdown on response, use pure text.""",
                },
            ],
        )

        response_post = response["choices"][0]["message"]["content"]
        print(f"Response post: {response_post}")

        return response_post

    @start()
    def categorize(self, request: str = None):
        print("Triggered 'categorize'")
        request_text = request or self.request

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that takes a client input for social media posts and categorizes it. Return a JSON file WITHOUT QUOTES and json word on it, with the following structure: {\"category\": \"<sermon_or_post-idea_or_bible-verse>\", \"sub_category\": \"<sub_category>\", \"require_development\": <true_or_false>, \"bible_verse\": <verse_or_empty-string>}.",
                },
                {
                    "role": "user",
                    "content": request_text,
                },
            ],
        )

        category = response["choices"][0]["message"]["content"]
        print(f"Category: {category}")

        return category

    @listen(or_(categorize, categorize_pro))
    def check_categorization(self, category):
        print("Triggered 'check_categorization'")
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""Check if the content on {self.request} is correctly categorized as {category}. Return a JSON file WITHOUT QUOTES and json word on it, with the following structure: {{"correct": true}} or {{"correct": false}}.""",
                },
            ],
        )

        response_check = response["choices"][0]["message"]["content"]
        print(f"Response check: {response_check}")

        return category, response_check

    @listen(check_categorization)
    def process_request(self, result):
        category, response_check = result
        response_check = json.loads(response_check)
        
        if not response_check["correct"]:
            self.categorize_pro(self.request)
            return

        category = json.loads(category)
        
        if category["require_development"]:
            developed_idea = self.develop_idea(self.request)
        else:
            developed_idea = self.request
        
        if category["bible_verse"] == "":
            bible_verse = self.extract_bible_verse(developed_idea)
        else:
            bible_verse = category["bible_verse"]

        post = self.generate_post(developed_idea, category["sub_category"], bible_verse)
        print("============================= POST =============================")
        print(post)
        print("============================= POST =============================")


request = """
    O sermão aborda a importância da gratidão, especialmente para os jovens, que muitas vezes se perdam em queixas. 
    O pregador incentiva a reflexão sobre as bênçãos recebidas, como a liberdade religiosa, a amizade cristã, as oportunidades 
    de crescimento espiritual e o ministério jovem. Ele expressa gratidão por esses jovens, vendo-os como prova da ação de Deus. 
    
    Baseando-se em Colossenses 1, a mensagem central destaca a gratidão a Deus por nos tornar dignos de participar da herança 
    dos santos, pela salvação do domínio das trevas e pela entrada no reino do Filho amado. A gratidão deve impactar passado, 
    presente e futuro, manifestando-se em ações.
    
    A salvação em Cristo é comparada à libertação do império das trevas para o reino de Deus, similar à luta entre o bem e o mal. 
    Cristo nos resgatou da escravidão, trazendo liberdade e preenchendo o coração com amor e gratidão. Essa libertação, comparada 
    à quitação de uma dívida impossível, nos concede a morada eterna.
    
    A gratidão deve nos motivar a conhecer mais a história da salvação. A mensagem reforça a importância da gratidão como estilo 
    de vida (Colossenses 3:15-17), expressa em palavras, ações e pensamentos, e destaca a continuidade do evangelho através das 
    gerações. A parábola dos dez leprosos (Lucas 10:11-19) ilustra a importância da gratidão expressa em ações.
    
    A gratidão deve ser dirigida a Deus, a Jesus Cristo, e cultivada como virtude, principalmente pelos jovens. O pregador propõe 
    a troca do "muro das lamentações" pela "corda da gratidão", um registro escrito das bênçãos recebidas. Mesmo em dificuldades, 
    como exames, a gratidão deve permanecer.
    
    O pregador compartilha sua experiência com decepções em amizades, enfatizando que Deus usa essas situações para nos proteger 
    e ensinar. A gratidão nos permite confiar em Deus, mesmo sem entender o propósito do sofrimento (Romanos 8:28). Deus age mesmo 
    enquanto dormimos (Salmos 4:8). A gratidão é um testemunho ao mundo (Colossenses 4:2-5).
    
    O exemplo de Paulo e Silas (Atos 16), que louvaram a Deus na prisão, demonstra o poder transformador da gratidão. O pregador 
    incentiva a congregação a ser uma geração de gratidão, refletindo a transformação divina.
    
    O sermão conclui com uma oração de gratidão pelos jovens, pedindo que se tornem um "recital de gratidão", expressando em 
    palavras e ações o amor por Deus. A oração final inclui pedidos de bênçãos, proteção e fortalecimento espiritual para os 
    jovens, para que se tornem anunciadores da paz e da verdade, cooperando na obra de salvação.
    
    O sermão termina com uma oração pela Igreja em todo o mundo e um convite para uma ceia comunitária.
    
    Referências bíblicas:
    - Colossenses 1
    - Colossenses 3:15-17
    - Lucas 10:11-19
    - Romanos 8:28
    - Salmos 4:8
    - Colossenses 4:2-5
    - Atos 16
    """

request2 = """atos 2"""
flow = ProcessRequestFlow(request=request)
result = flow.kickoff()  
