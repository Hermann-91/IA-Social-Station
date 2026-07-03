# IA Social Station: Centro de Comando de Conteúdo

## Visão Geral do Projeto
O **IA Social Station** é uma ferramenta de geração de conteúdo impulsionada por IA, projetada para ajudar criadores do Instagram a planejar suas postagens de forma eficiente, evitando os riscos associados à postagem automatizada (shadowbanning). Ele utiliza os modelos **Google Gemini** para pesquisar tendências, escrever legendas envolventes e criar prompts de alta qualidade para geração de imagens.

A filosofia central é "Execução Manual, Insight de IA": use a IA para o trabalho pesado de pesquisa e rascunho criativo, mas mantenha o controle humano sobre o processo final de upload.

### Principais Tecnologias
- **Python 3.12+**
- **Streamlit**: Interface web para os "Cards de Conteúdo".
- **Google GenAI SDK**: Responsável pela geração de conteúdo via `gemini-2.5-flash`.
- **python-dotenv**: Para gerenciamento seguro de chaves de API.
- **Pillow**: Para processamento e manipulação de imagens.

---

## Estrutura do Projeto
- `app.py`: O ponto de entrada principal. Orquestra a interface Streamlit, lida com a interação do usuário e renderiza os cards de conteúdo.
- `engine.py`: A camada de lógica. Contém a engenharia de prompts e a integração da API com o Google Gemini.
- `outputs/`: Diretório destinado ao armazenamento de ativos gerados e logs.
- `.env`: Arquivo de configuração para variáveis de ambiente sensíveis (ex: `GEMINI_API_KEY`).
- `requirements.txt`: Lista todas as dependências do Python.
- `gemini.md`: Contém brainstorms do projeto, rascunhos arquitetônicos e notas de desenvolvimento (referência histórica).

---

## Construção e Execução

### Pré-requisitos
1.  **Python 3.12** ou superior.
2.  **Chave de API do Gemini**: Obtenha uma no [Google AI Studio](https://aistudio.google.com/).

### Instalação
1.  Clone o repositório e navegue até o diretório do projeto.
2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
3.  Instale os pacotes necessários:
    ```bash
    pip install -r requirements.txt
    ```

### Configuração
Crie um arquivo `.env` no diretório raiz e adicione sua chave de API:
```env
GEMINI_API_KEY=sua_chave_api_aqui
```

### Executando a Aplicação
Inicie o painel do Streamlit:
```bash
streamlit run app.py
```
A aplicação estará disponível em `http://localhost:8501`.

---

## Convenções de Desenvolvimento

### Arquitetura
- **Separação de Preocupações**: Mantenha a lógica de UI no `app.py` e a lógica de interação com o modelo no `engine.py`.
- **Engenharia de Prompts**: Atualizações no comportamento de geração devem ser feitas no `engine.py`, refinando a variável `prompt_texto`.

### Formatação e Estilo
- **Formatação Estrita**: O `engine.py` depende de um formato específico baseado em tags (`---INICIO---`, `LEGENDA:`, etc.) para analisar a saída do Gemini. Certifique-se de que qualquer alteração no prompt mantenha essa estrutura ou atualize o analisador (parser) de acordo.
- **Verificação Manual**: Sempre teste a geração de conteúdo após alterar os prompts para garantir que a lógica de fallback não seja acionada desnecessariamente.

### Próximos Passos (Roadmap)
- [ ] Integração com Nano Banana 2 (Flash Image) para geração direta de imagens dentro do app.
- [ ] Suporte para múltiplas plataformas de mídia social (TikTok, X).
- [ ] Recurso "Salvar nos Favoritos" com armazenamento local na pasta `outputs/`.
