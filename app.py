import streamlit as st
import os
from engine import gerar_conteudo_completo, gerar_comentario_contextual, gerar_hashtags_estrategicas
from chrome_agent import DepuradorChrome, AutomatizadorInstagram
from gemini_service import ServicoGemini

st.set_page_config(page_title="IA Social Station", layout="wide", page_icon="📸")

# CSS para cards elegantes
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 14px !important;
    }
    .prompt-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📸 IA Social Station")
st.subheader("Orquestração de Conteúdo e Automação de Divulgação com Inteligência Artificial.")

# Inicializa estados de sessão do Streamlit para manter dados entre cliques
if "captura" not in st.session_state:
    st.session_state.captura = None
if "comentario_gerado" not in st.session_state:
    st.session_state.comentario_gerado = ""
if "comentario_post" not in st.session_state:
    st.session_state.comentario_post = ""

# Criando as Abas da Interface (SOLID / Modularidade)
aba_divulgacao, aba_criar_post, aba_hashtags = st.tabs([
    "🤖 Divulgação Ativa (Chrome)", 
    "🚀 Criar & Publicar Post", 
    "#️⃣ Hashtags em Alta"
])

# ----------------- ABA 1: DIVULGAÇÃO INTELIGENTE (CHROME) -----------------
with aba_divulgacao:
    st.markdown("## 🤖 Módulo de Divulgação Cooperativa (Instagram)")
    st.markdown(
        "Use o Google Chrome aberto na porta `9222`. Ao encontrar um post relevante sobre motoristas de aplicativo, "
        "selecione o texto da reclamação com o mouse na tela e utilize o painel abaixo para capturar e automatizar."
    )
    
    col_acoes, col_visualizacao = st.columns([1, 1])
    
    with col_acoes:
        st.markdown("### 🛠️ Ações de Automação")
        
        btn_capturar = st.button("🔌 Capturar Aba Ativa do Chrome", use_container_width=True)
        
        if btn_capturar:
            with st.spinner("Conectando ao Chrome e capturando estado..."):
                try:
                    depurador = DepuradorChrome()
                    automatizador = AutomatizadorInstagram(depurador)
                    dados = automatizador.capturar_post_e_tela()
                    st.session_state.captura = dados
                    st.success("Estado da aba do Chrome capturado com sucesso!")
                except Exception as e:
                    st.error(f"Erro na conexão com o Chrome: {e}")
                    st.info("Dica: Certifique-se de que o Chrome de depuração está aberto com a porta 9222 ativa.")
        
        if st.session_state.captura:
            dados = st.session_state.captura
            st.markdown("#### 📄 Informações do Post Capturado")
            st.text_input("Título da Aba", value=dados["titulo"], disabled=True)
            st.text_input("URL Ativa", value=dados["url"], disabled=True)
            
            # Campo de seleção de texto
            texto_sel = dados["texto_selecionado"]
            if not texto_sel:
                st.warning("Nenhum texto estava selecionado com o mouse na tela. A IA usará o título da aba como contexto.")
                texto_sel = dados["titulo"]
                
            st.text_area("Texto Selecionado na Tela", value=texto_sel, height=120, disabled=True)
            
            # Ação de Geração IA
            btn_gerar_comment = st.button("✨ Gerar Comentário Inteligente com IA", use_container_width=True)
            
            if btn_gerar_comment:
                with st.spinner("Gemini gerando comentário contextualizado (Análise Multimodal ativa)..."):
                    try:
                        comment = gerar_comentario_contextual(texto_sel)
                        st.session_state.comentario_gerado = comment
                        st.success("Comentário gerado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao gerar com o Gemini: {e}")
            
            # Editor do comentário gerado
            if st.session_state.comentario_gerado:
                comentario_revisado = st.text_area(
                    "📝 Revise e edite o comentário antes de postar:",
                    value=st.session_state.comentario_gerado,
                    height=180
                )
                
                # Ação de Postagem
                btn_postar = st.button("🚀 Publicar Comentário no Chrome", use_container_width=True)
                
                if btn_postar:
                    with st.spinner("Enviando comentário e submetendo no Chrome..."):
                        try:
                            depurador = DepuradorChrome()
                            automatizador = AutomatizadorInstagram(depurador)
                            msg = automatizador.enviar_comentario(comentario_revisado)
                            st.success(f"Sucesso! {msg}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Falha ao enviar comentário: {e}")
                            
    with col_visualizacao:
        st.markdown("### 🖼️ Visualização do Navegador")
        if st.session_state.captura and st.session_state.captura.get("caminho_screenshot"):
            caminho_img = st.session_state.captura["caminho_screenshot"]
            if os.path.exists(caminho_img):
                st.image(caminho_img, caption="Print capturado da sua aba do Chrome", use_container_width=True)
            else:
                st.info("Nenhuma imagem de captura disponível.")
        else:
            st.info("Clique em 'Capturar Aba Ativa' para obter a visualização em tempo real do seu Chrome.")

# ----------------- ABA 2: CRIAR & PUBLICAR POST (NOVO) -----------------
with aba_criar_post:
    st.markdown("## 🚀 Criador & Publicador de Posts (Imagem, Carrossel ou Reels)")
    st.markdown("Faça o upload da sua mídia e gere legendas inteligentes com a IA para publicação automática no Chrome.")
    
    col_upload, col_ia = st.columns([1, 1])
    
    with col_upload:
        st.markdown("### 🖼️ Mídia do Post")
        tipo_midia = st.radio("Tipo de publicação:", ["Imagens (Única ou Carrossel)", "Reels (Vídeo)"])
        
        arquivos_midia = []
        if tipo_midia == "Reels (Vídeo)":
            arquivo = st.file_uploader("Selecione o vídeo do Reels (MP4/MOV):", type=["mp4", "mov"], key="video_reels")
            if arquivo:
                arquivos_midia = [arquivo]
        else:
            # Permite selecionar múltiplos arquivos de imagem por padrão
            arquivos = st.file_uploader(
                "Selecione as imagens do post (selecione uma ou mais para Carrossel):", 
                type=["png", "jpg", "jpeg"], 
                accept_multiple_files=True,
                key="imagens_post"
            )
            if arquivos:
                arquivos_midia = arquivos
                
        prompt_custom = st.text_area(
            "Ideias/Instruções para o post (opcional):",
            placeholder="Ex: Diga que este app é gratuito e ajuda o motorista a economizar no combustível.",
            key="prompt_post_criar"
        )
        
        # Salva caminhos locais para o upload
        caminhos_salvos = []
        if arquivos_midia:
            os.makedirs("outputs", exist_ok=True)
            for idx, arq in enumerate(arquivos_midia):
                ext = arq.name.split(".")[-1]
                caminho_local = os.path.join(os.getcwd(), "outputs", f"upload_temp_{idx}.{ext}")
                with open(caminho_local, "wb") as f:
                    f.write(arq.read())
                caminhos_salvos.append(caminho_local)
                
    with col_ia:
        st.markdown("### ✍️ Legenda IA & Publicação")
        
        btn_gerar_legenda = st.button("✨ Analisar Mídia & Gerar Legenda", use_container_width=True, key="btn_gerar_legenda_post")
        
        if btn_gerar_legenda:
            if not caminhos_salvos:
                st.error("Por favor, selecione as imagens ou vídeo primeiro!")
            else:
                with st.spinner("IA analisando as imagens e estruturando legenda..."):
                    try:
                        from PIL import Image as PILImage
                        # Abre a primeira imagem para análise visual do Gemini (multimodal)
                        img_analise = PILImage.open(caminhos_salvos[0])
                        
                        servico = ServicoGemini()
                        legenda_gerada = servico.gerar_legenda_de_imagem(img_analise, prompt_custom)
                        st.session_state.comentario_post = legenda_gerada
                        st.success("Legenda gerada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro na IA do Gemini: {e}")
                        
        if st.session_state.comentario_post:
            legenda_revisada = st.text_area(
                "📝 Revise o texto antes de publicar:",
                value=st.session_state.comentario_post,
                height=220,
                key="legenda_post_revisao"
            )
            
            btn_publicar_post = st.button("🚀 Publicar Automático no Instagram", use_container_width=True)
            
            if btn_publicar_post:
                with st.spinner("Conectando ao Chrome e iniciando upload automático..."):
                    try:
                        depurador = DepuradorChrome()
                        automatizador = AutomatizadorInstagram(depurador)
                        status_pub = automatizador.publicar_post_instagram(caminhos_salvos, legenda_revisada)
                        st.success(f"Status: {status_pub}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Falha ao realizar publicação automática: {e}")

# ----------------- ABA 3: PESQUISADOR DE HASHTAGS -----------------
with aba_hashtags:
    st.markdown("## #️⃣ Gerador de Hashtags Estratégicas")
    st.markdown("Pesquise e extraia rapidamente as hashtags de maior engajamento para qualquer nicho.")
    
    tema_hash = st.text_input("Insira o tema/nicho para busca:", placeholder="Ex: Motorista de Aplicativo", key="tema_hash_input")
    qtd_hash = st.slider("Quantidade de hashtags sugeridas:", 5, 20, 10, key="qtd_hash_slider")
    btn_gerar_hash = st.button("🔍 Pesquisar Hashtags", use_container_width=True, key="btn_gerar_hash")
    
    if btn_gerar_hash:
        if not tema_hash:
            st.error("Por favor, digite um tema para a pesquisa!")
        else:
            with st.spinner(f"Analisando métricas de engajamento para '{tema_hash}'..."):
                try:
                    resultado_hash = gerar_hashtags_estrategicas(tema_hash, qtd_hash)
                    st.markdown("### 📈 Hashtags Sugeridas:")
                    st.info(resultado_hash)
                except Exception as e:
                    st.error(f"Erro ao obter hashtags: {e}")
