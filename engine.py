import os
from google import genai
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

def gerar_conteudo_completo(tema, quantidade=1):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env. Crie um arquivo .env com sua chave.")
        
    client = genai.Client(api_key=api_key)
    resultados = []

    for i in range(quantidade):
        # Prompt otimizado para as novas regras
        prompt_texto = (
            f"Aja como um estrategista de conteúdo e criador de personagem para Instagram. Analise tendências atuais sobre: {tema}.\n\n"
            f"Gere 1 post contendo:\n"
            f"1. LEGENDA: Um texto viral, envolvente, com quebras de linha e emojis.\n"
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
            res = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt_texto
            )
            
            texto_puro = res.text
            
            # Extração dos blocos
            try:
                legenda = texto_puro.split("LEGENDA:")[1].split("HASHTAGS:")[0].strip()
                hashtags = texto_puro.split("HASHTAGS:")[1].split("PROMPT_IMAGEM:")[0].strip()
                prompt_img = texto_puro.split("PROMPT_IMAGEM:")[1].split("---FIM---")[0].strip()
            except:
                # Fallback caso o modelo fuja da formatação
                legenda = "Erro na formatação. Verifique o texto gerado."
                hashtags = "#ia #tech #instagram #trend #criatividade"
                prompt_img = f"Professional photography of {tema}, cinematic lighting, 8k, instagram style."

            resultados.append({
                "legenda_completa": f"{legenda}\n\n.\n.\n.\n{hashtags}",
                "prompt_usado": prompt_img,
                "tema": tema
            })
            
        except Exception as e:
            print(f"Erro no Gemini: {e}")
            continue
        
    return resultados


def gerar_comentario_contextual(post_texto):
    """
    Usa o Gemini para gerar um comentário empático, contextualizado e não-spam
    para divulgar o App Gestão Motora a partir de uma postagem capturada do Instagram.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env. Crie um arquivo .env com sua chave.")
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"Você é um motorista de aplicativo experiente rodando no dia a dia e quer ajudar outros motoristas.\n"
            f"Analise o seguinte post/desabafo de um motorista no Instagram:\n\n"
            f"\"\"\"\n{post_texto}\n\"\"\"\n\n"
            f"Gere um comentário curto (máximo de 3 parágrafos pequenos), empático, amigável e com tom de depoimento real "
            f"para responder a esse post. No meio do texto, recomende de forma sutil e natural o aplicativo de gestão "
            f"que você usa para planejar custos de combustível, manutenção e calcular o real lucro: "
            f"o 'App Gestão Motora' com o link (https://produtostops.online/app.gestaomotora/).\n\n"
            f"Evite parecer spam ou propaganda forçada. Fale na primeira pessoa do singular (eu), use quebras de linha e no máximo 1 ou 2 emojis."
        )
        
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return res.text.strip()
    except Exception as e:
        print(f"Erro no Gemini ao gerar comentário: {e}")
        return (
            "Complicado, irmão! O dia a dia na pista é cansativo e com tarifa baixa fica difícil ver lucro de verdade. "
            "Eu comecei a usar o App Gestão Motora (https://produtostops.online/app.gestaomotora/) pra me ajudar "
            "a calcular o real lucro por km rodado e planejar minhas despesas. Tem ajudado muito! Tamo junto e boa rodagem! 🚗🤜🤛"
        )
