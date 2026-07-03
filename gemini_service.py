import os
from google import genai
from PIL import Image

class ServicoGemini:
    """
    Responsabilidade: Gerenciar todos os serviços e integrações com o modelo Google Gemini.
    Princípio: SRP (Single Responsibility Principle) - Focado unicamente na lógica de IA.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no ambiente. Configure seu arquivo .env.")
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            self.client = None
            print(f"Erro ao inicializar o cliente do Gemini: {e}")
        self.modelo_padrao = "gemini-2.5-flash"

    def gerar_estrategia_post(self, tema: str, quantidade: int = 1) -> list:
        """Gere estratégias de posts completos para o Instagram (imagem + legenda)."""
        if not self.client:
            print("Erro: Cliente do Gemini não inicializado.")
            return []
            
        resultados = []
        for i in range(quantidade):
            prompt = (
                f"Aja como um estrategista de conteúdo e criador de personagem para Instagram. Analise tendências atuais sobre: {tema}.\n\n"
                f"Gere 1 post contendo:\n"
                f"1. LEGENDA: Um texto viral, envolvendo, com quebras de linha e emojis.\n"
                f"2. HASHTAGS: Exatamente 5 hashtags estratégicas e em alta.\n"
                f"3. PROMPT_IMAGEM: Um prompt detalhado em inglês para uma IA de geração de imagem (como Midjourney ou Imagen 3). "
                f"O prompt deve descrever uma cena ultra-realista, estilo fotografia profissional, biotipo atletico, aspecto 4:5, que ilustre perfeitamente o post.\n\n"
                f"Formate a resposta rigorosamente assim:\n"
                f"---INICIO---\n"
                f"LEGENDA: [texto]\n"
                f"HASHTAGS: [as 5 hashtags]\n"
                f"PROMPT_IMAGEM: [prompt em inglês]\n"
                f"---FIM---"
            )
            
            try:
                res = self.client.models.generate_content(
                    model=self.modelo_padrao,
                    contents=prompt
                )
                texto_puro = res.text
                
                try:
                    legenda = texto_puro.split("LEGENDA:")[1].split("HASHTAGS:")[0].strip()
                    hashtags = texto_puro.split("HASHTAGS:")[1].split("PROMPT_IMAGEM:")[0].strip()
                    prompt_img = texto_puro.split("PROMPT_IMAGEM:")[1].split("---FIM---")[0].strip()
                except Exception:
                    legenda = "Erro na formatação automática da resposta do Gemini."
                    hashtags = "#ia #tech #instagram #trend #criatividade"
                    prompt_img = f"Professional photography of {tema}, cinematic lighting, 8k, instagram style."

                resultados.append({
                    "legenda_completa": f"{legenda}\n\n.\n.\n.\n{hashtags}",
                    "prompt_usado": prompt_img,
                    "tema": tema
                })
            except Exception as e:
                print(f"Erro ao gerar post {i+1}: {e}")
                continue
        return resultados

    def gerar_hashtags_estrategicas(self, tema: str, quantidade: int = 10) -> str:
        """Minera e categoriza as hashtags de maior engajamento para um nicho específico."""
        if not self.client:
            return "⚠️ Erro: Cliente do Gemini não inicializado."
            
        prompt = (
            f"Aja como um especialista em SEO e crescimento orgânico no Instagram.\n"
            f"Analise o tema/nicho: {tema}.\n"
            f"Gere uma lista de exatamente {quantidade} hashtags estratégicas que mais engajam para este nicho.\n\n"
            f"Divida as hashtags em 3 categorias claras:\n"
            f"1. Hashtags de Nicho (específicas para o tema)\n"
            f"2. Hashtags de Público-Alvo (quem consumiria esse conteúdo)\n"
            f"3. Hashtags de Alta Relevância (gerais do setor, mas quentes)\n\n"
            f"Forneça a resposta em formato amigável de lista com emojis, sem blocos markdown complexos."
        )
        try:
            res = self.client.models.generate_content(
                model=self.modelo_padrao,
                contents=prompt
            )
            return res.text.strip()
        except Exception as e:
            return f"⚠️ Erro ao obter hashtags do Gemini: {e}"

    def gerar_comentario_contextual(self, texto_post: str, caminho_imagem: str = None) -> str:
        """
        Gera um comentário de divulgação empático a partir do texto e do print de tela do post (Multimodal).
        """
        prompt = (
            f"Você é um motorista de aplicativo experiente rodando no dia a dia e quer ajudar outros motoristas.\n"
            f"Analise o seguinte post/desabafo de um motorista no Instagram:\n\n"
            f"\"\"\"\n{texto_post}\n\"\"\"\n\n"
            f"Gere um comentário curto (máximo de 3 parágrafos pequenos), empático, amigável e com tom de depoimento real "
            f"para responder a esse post. No meio do texto, recomende de forma sutil e natural o aplicativo de gestão "
            f"que você usa para planejar custos de combustível, manutenção e calcular o real lucro: "
            f"o 'App Gestão Motora' com o link (https://produtostops.online/app.gestaomotora/).\n\n"
            f"Evite parecer spam ou propaganda forçada. Fale na primeira pessoa do singular (eu), use quebras de linha e no máximo 1 ou 2 emojis."
        )
        
        elementos_conteudo = []
        
        # Integração Multimodal: Se houver print do Chrome, enviamos a imagem para análise da IA
        if caminho_imagem and os.path.exists(caminho_imagem):
            try:
                img = Image.open(caminho_imagem)
                elementos_conteudo.append(img)
                prompt += "\nUtilize também a imagem anexada do post para extrair o contexto visual e entender melhor o que o criador está mostrando."
            except Exception as e:
                print(f"Erro ao carregar imagem para análise multimodal: {e}")
                
        elementos_conteudo.append(prompt)
        
        try:
            if not self.client:
                raise ValueError("Cliente do Gemini não inicializado.")
                
            res = self.client.models.generate_content(
                model=self.modelo_padrao,
                contents=elementos_conteudo
            )
            return res.text.strip()
        except Exception as e:
            print(f"Erro ao gerar comentário: {e}")
            return (
                "Complicado, irmão! O dia a dia na pista é cansativo e com tarifa baixa fica difícil ver lucro de verdade. "
                "Eu comecei a usar o App Gestão Motora (https://produtostops.online/app.gestaomotora/) pra me ajudar "
                "a calcular o real lucro por km rodado e planejar minhas despesas. Tem ajudado muito! Tamo junto e boa rodagem! 🚗🤜🤛"
            )

    def gerar_legenda_de_imagem(self, imagem_pillow: Image, contexto_nicho: str = None) -> str:
        """
        Analisa visualmente a imagem fornecida pelo usuário e cria legenda e hashtags adequadas (Multimodal).
        """
        if not self.client:
            return "⚠️ Erro: Cliente do Gemini não inicializado."
            
        prompt = (
            "Analise visualmente esta imagem e escreva uma legenda de alta performance para o Instagram.\n\n"
            "Requisitos da legenda:\n"
            "1. Crie um título chamativo que prenda a atenção nos primeiros 3 segundos.\n"
            "2. Desenvolva um texto envolvente, amigável e focado em gerar conexão (perguntas no final).\n"
            "3. Adicione quebras de linha adequadas e emojis estratégicos.\n"
            "4. Inclua exatamente 5 hashtags de engajamento no final do texto.\n"
        )
        if contexto_nicho:
            prompt += f"\nAdapte a legenda para o seguinte nicho/contexto sugerido pelo usuário: {contexto_nicho}.\n"
            
        try:
            res = self.client.models.generate_content(
                model=self.modelo_padrao,
                contents=[imagem_pillow, prompt]
            )
            return res.text.strip()
        except Exception as e:
            return f"⚠️ Erro ao analisar a imagem no Gemini: {e}"
