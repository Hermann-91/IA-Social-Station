import os
from dotenv import load_dotenv
from gemini_service import ServicoGemini

# Carrega variáveis do arquivo .env
load_dotenv()

def gerar_conteudo_completo(tema, quantidade=1):
    """Fachada (Facade) para manter compatibilidade com a aba de cards de posts."""
    servico = ServicoGemini()
    return servico.gerar_estrategia_post(tema, quantidade)

def gerar_comentario_contextual(post_texto):
    """Fachada (Facade) para manter compatibilidade com a automação do Chrome."""
    servico = ServicoGemini()
    # Tenta usar a captura de tela salva localmente como contexto multimodal
    caminho_imagem = os.path.join("outputs", "instagram_capture.png")
    return servico.gerar_comentario_contextual(post_texto, caminho_imagem)

def gerar_hashtags_estrategicas(tema, quantidade=10):
    """Fachada (Facade) para a pesquisa de hashtags em alta."""
    servico = ServicoGemini()
    return servico.gerar_hashtags_estrategicas(tema, quantidade)
