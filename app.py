import streamlit as st
import os
from engine import gerar_conteudo_completo, gerar_comentario_contextual
from chrome_agent import DepuradorChrome, AutomatizadorInstagram

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

# Criando as Abas da Interface
aba_posts, aba_divulgacao = st.tabs(["📝 Criador de Cards de Conteúdo", "🤖 Divulgação Inteligente (Chrome)"])

with aba_posts:
    with st.sidebar:
        st.header("Configurações do Post")
        tema = st.text_input("Qual o tema/nicho?", placeholder="Ex: Minimalismo Digital", key="tema_posts")
        qtd = st.slider("Quantos posts planejar?", 1, 5, 1, key="qtd_posts")
        botao = st.button("Gerar Estratégia", use_container_width=True, key="btn_gerar_posts")
        
        st.divider()
        st.info("Este modelo foca em gerar o **Prompt Visual** perfeito e a **Legenda Otimizada** com 5 hashtags.")

    if botao:
        if not tema:
            st.error("Por favor, insira um tema!")
        else:
            with st.spinner(f"Analisando tendências para '{tema}'..."):
                try:
                    posts = gerar_conteudo_completo(tema, qtd)
                    
                    if not posts:
                        st.warning("Não foi possível gerar conteúdo agora.")
                    else:
                        for idx, post in enumerate(posts):
                            with st.container():
                                st.markdown(f"## 📝 Post {idx + 1} - Tema: {post['tema']}")
                                
                                col1, col2 = st.columns([1, 1])
                                
                                with col1:
                                    st.markdown("### 🖼️ Prompt para Imagem")
                                    st.info("Use este prompt no Midjourney, Leonardo.ai ou Gemini para gerar sua imagem:")
                                    st.code(post["prompt_usado"], language="text")
                                    st.success("Dica: Imagens em aspecto 4:5 performam melhor no feed.")

                                with col2:
                                    st.markdown("### ✍️ Legenda + Hashtags (Máx 5)")
                                    st.text_area(
                                        "Copie para o Instagram:",
                                        post["legenda_completa"],
                                        height=250,
                                        key=f"txt_{idx}"
                                    )
                                    st.caption("As 5 hashtags estão incluídas ao final do texto.")
                                
                                st.divider()
                                    
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

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
                with st.spinner("Gemini gerando comentário contextualizado..."):
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
