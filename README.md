# 📸 IA Social Station: Centro de Comando de Conteúdo

O **IA Social Station** é um painel inteligente de orquestração de conteúdo e automação cooperativa para o Instagram. Ele utiliza os modelos generativos **Google Gemini** para criar legendas virais, analisar imagens de forma multimodal e automatizar publicações e divulgação em tempo real no navegador Chrome via WebSocket (CDP).

A filosofia central do projeto é **"Insight de IA, Execução Local"**: use o poder da IA para processar mídias e gerar interações contextuais, mantendo o controle total sobre a navegação para evitar os riscos de shadowbanning de APIs não oficiais.

---

## 🚀 Funcionalidades Principais

*   🤖 **Divulgação Cooperativa (Chrome Control):** Conecta-se à aba ativa do Instagram no Chrome, captura o post de terceiros (imagem + texto) e gera um comentário empático e contextualizado pelo Gemini para divulgar o seu produto.
*   🚀 **Criador de Posts em Lote (1 a 4 mídias):** Configure e planeje múltiplos posts de uma vez. O app suporta Imagem Única, Carrosséis (múltiplas imagens) e Reels (vídeo).
*   📅 **Agendador Automático em Background:** Possui uma thread em segundo plano nativa que monitora a fila de postagens local. No horário agendado, o robô faz o upload da mídia e publica o post automaticamente no Chrome.
*   📈 **Sugestão de Horários de Pico:** A IA analisa a sua imagem e sugere o melhor horário estratégico de publicação baseado no público-alvo do seu nicho.
*   #️⃣ **Pesquisa Rápidas de Hashtags:** Um gerador dedicado para extrair e categorizar as hashtags mais quentes do nicho em alta relevância, nicho específico e público-alvo.

---

## 🏛️ Arquitetura do Projeto (Clean Architecture & SOLID)

O projeto foi reestruturado seguindo as melhores práticas de Engenharia de Software, desacoplando totalmente a interface, a automação e as APIs em camadas limpas em Português:

```text
├── nucleo/              # Entidades puras de negócio (Postagem)
├── repositorios/        # Persistência e gerenciamento da fila de dados local (JSON)
├── servicos/            # Casos de uso (Gemini, Fachada de Controle, Agendador background)
├── automacao/           # Conexão de baixo nível e interações de DOM com o Chrome (CDP)
├── apresentacao/        # Camada visual e telas da interface do usuário (Streamlit UI)
├── testes/              # Suite de testes unitários automatizados (pytest)
└── app.py               # Ponto de entrada simplificado da aplicação
```

---

## 🛠️ Configuração e Instalação

### Pré-requisitos
1.  **Python 3.12** ou superior.
2.  **Google Chrome instalado nativamente** (porta de depuração remota ativada).
3.  **Chave de API do Gemini:** Obtenha uma chave gratuita no [Google AI Studio](https://aistudio.google.com/).

### Passo a Passo de Execução

1.  **Clonar o repositório** e navegar até o diretório.
2.  **Configurar o Ambiente Virtual (venv) e dependências:**
    ```bash
    python3 -m venv venv
    venv/bin/pip install -r requirements.txt
    ```
3.  **Configurar Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto e insira a sua chave de API:
    ```env
    GEMINI_API_KEY=sua_chave_aqui
    ```

4.  **Iniciar o Navegador de Depuração (Chrome):**
    Feche todas as janelas comuns do Chrome e inicie a conexão de depuração com origens permitidas:
    ```bash
    google-chrome --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=$HOME/.config/antigravity-chrome-profile https://www.instagram.com/
    ```
    *Certifique-se de realizar o login na sua conta do Instagram nesta janela específica que se abriu.*

5.  **Iniciar o Painel do Robô (Streamlit):**
    ```bash
    venv/bin/streamlit run app.py
    ```
    O painel estará disponível em `http://localhost:8501`.

---

## 🧪 Suite de Testes
Para rodar todos os testes de unidade da arquitetura e garantir a integridade do robô, execute:
```bash
venv/bin/python -m pytest
```

---
Desenvolvido com ☕ e 🐍 por Hermann.
