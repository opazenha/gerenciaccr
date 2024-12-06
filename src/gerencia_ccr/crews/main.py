#!/usr/bin/env python
import sys
import warnings

from ingest_crew import IngestCrew
from media_crew import MediaCrew
from posts_crew import PostsCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    sermon = """
    O sermão aborda a importância da gratidão, especialmente para os jovens, que muitas vezes se perdem em queixas. 
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
    
    # inputs = {"content": sermon}
    # result = IngestCrew().ingest_crew().kickoff(inputs=inputs)
    # if result.pydantic:
    #     print(result.pydantic.json(indent=4))
    # else:
    #     print(result.raw)

    # inputs = {"content": sermon}
    # result = MediaCrew().media_crew().kickoff(inputs=inputs)
    # if result.pydantic:
    #     print(result.pydantic.json(indent=4))
    # else:
    #     print(result.raw)


        
if __name__ == "__main__":
    run()