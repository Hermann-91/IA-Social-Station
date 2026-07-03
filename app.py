import streamlit as st
import os
import json
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
                    st.info("Dica: Certifique-se de que o Chrome de depuração está aberto com a porta 9222 activa.")
        
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

# ----------------- ABA 2: CRIAR & PUBLICAR POST (LOTE E FILA) -----------------
with aba_criar_post:
    st.markdown("## 🚀 Fila de Planejamento e Publicação Automática")
    st.markdown("Configure até 4 posts em lote, receba sugestões de horários de pico baseados no nicho e envie as publicações para a sua fila.")
    
    # Carrega/Inicializa a fila local
    caminho_fila = os.path.join("outputs", "fila_postagens.json")
    fila = []
    if os.path.exists(caminho_fila):
        try:
            with open(caminho_fila, "r") as f:
                fila = json.load(f)
        except:
            fila = []

    st.markdown("### ✍️ Configurar Novo Lote")
    quantidade_posts = st.number_input("Quantos posts deseja planejar neste lote?", 1, 4, 1, key="qtd_posts_lote")
    
    # Abas dinâmicas para configuração
    abas_lote = st.tabs([f"Post {i+1}" for i in range(quantidade_posts)])
    configs_lote = []
    
    for idx, aba in enumerate(abas_lote):
        with aba:
            col_lote_file, col_lote_prompt = st.columns([1, 1])
            with col_lote_file:
                tipo_post_lote = st.radio(f"Formato (Post {idx+1}):", ["Imagens (Única/Carrossel)", "Reels (Vídeo)"], key=f"tipo_post_lote_{idx}")
                
                if tipo_post_lote == "Reels (Vídeo)":
                    imagens_lote = st.file_uploader(
                        f"Selecione o vídeo (Post {idx+1}):", 
                        type=["mp4", "mov"],
                        accept_multiple_files=False,
                        key=f"mídia_lote_video_{idx}"
                    )
                    imagens_lote = [imagens_lote] if imagens_lote else []
                else:
                    imagens_lote = st.file_uploader(
                        f"Selecione as mídias (Post {idx+1}):", 
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                        key=f"mídia_lote_img_{idx}"
                    )
            with col_lote_prompt:
                prompt_lote = st.text_area(
                    f"Instruções/Nicho (Post {idx+1}):", 
                    placeholder="Ex: Nicho de motoristas, falar sobre custos de combustível.",
                    key=f"prompt_lote_{idx}"
                )
            configs_lote.append({"midias": imagens_lote, "prompt": prompt_lote})
            
    btn_gerar_lote = st.button("✨ Gerar Planejamento de Lote com IA", use_container_width=True)
    
    if btn_gerar_lote:
        erros = []
        posts_novos = []
        
        for i, config in enumerate(configs_lote):
            if not config["midias"]:
                erros.append(f"Mídia do Post {i+1} não foi selecionada.")
                continue
                
            # Salva mídias locais
            os.makedirs("outputs", exist_ok=True)
            caminhos_locais = []
            for j, arq in enumerate(config["midias"]):
                ext = arq.name.split(".")[-1]
                caminho_local = os.path.join(os.getcwd(), "outputs", f"lote_temp_{len(fila) + i}_{j}.{ext}")
                with open(caminho_local, "wb") as f:
                    f.write(arq.read())
                caminhos_locais.append(caminho_local)
                
            # IA gera legenda e horário
            with st.spinner(f"Processando Post {i+1} no Gemini..."):
                try:
                    from PIL import Image as PILImage
                    # Usamos a primeira foto para análise visual multimodal
                    img_analise = PILImage.open(caminhos_locais[0])
                    servico = ServicoGemini()
                    resultado_ia = servico.gerar_legenda_e_horario(img_analise, config["prompt"])
                    
                    posts_novos.append({
                        "id": len(fila) + len(posts_novos) + 1,
                        "caminhos_mídias": caminhos_locais,
                        "legenda": resultado_ia["legenda"],
                        "horario_sugerido": resultado_ia["horario"],
                        "status": "Aguardando postagem"
                    })
                except Exception as e:
                    erros.append(f"Erro no Post {i+1}: {e}")
                    
        if erros:
            for err in erros:
                st.error(err)
        if posts_novos:
            fila.extend(posts_novos)
            with open(caminho_fila, "w") as f:
                json.dump(fila, f, indent=4)
            st.success(f"{len(posts_novos)} posts gerados e adicionados à fila local com sucesso!")
            
    st.divider()
    st.markdown("### 🗂️ Fila de Publicações Prontas")
    
    if not fila:
        st.info("Nenhuma publicação planejada na fila no momento.")
    else:
        for idx, post in enumerate(fila):
            with st.expander(f"Post {idx+1} - Horário sugerido: {post['horario_sugerido']} ({post['status']})"):
                col_prev, col_detalhes = st.columns([1, 2])
                with col_prev:
                    # Mostra a miniatura do post se for imagem
                    if post["caminhos_mídias"] and os.path.exists(post["caminhos_mídias"][0]):
                        ext = post["caminhos_mídias"][0].split(".")[-1].lower()
                        if ext in ["png", "jpg", "jpeg"]:
                            st.image(post["caminhos_mídias"][0], use_container_width=True)
                        else:
                            st.info("Mídia de Vídeo (Reels)")
                with col_detalhes:
                    legenda_ed = st.text_area(f"Texto da publicação:", value=post["legenda"], key=f"legenda_ed_{idx}", height=150)
                    
                    # Botões de Ação
                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        btn_postar_fila = st.button("🚀 Publicar Agora", key=f"btn_pub_fila_{idx}", use_container_width=True)
                    with col_btn2:
                        btn_remover_fila = st.button("❌ Remover da Fila", key=f"btn_rem_fila_{idx}", use_container_width=True)
                        
                    if btn_postar_fila:
                        with st.spinner("Automação ativa... Publicando no Instagram..."):
                            try:
                                depurador = DepuradorChrome()
                                automatizador = AutomatizadorInstagram(depurador)
                                res_pub = automatizador.publicar_post_instagram(post["caminhos_mídias"], legenda_ed)
                                st.success(f"Status: {res_pub}")
                                # Atualiza status
                                fila[idx]["status"] = "Postado"
                                with open(caminho_fila, "w") as f:
                                    json.dump(fila, f, indent=4)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao postar: {e}")
                                
                    if btn_remover_fila:
                        fila.pop(idx)
                        with open(caminho_fila, "w") as f:
                            json.dump(fila, f, indent=4)
                        st.success("Post removido da fila local.")
                        st.rerun()

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
