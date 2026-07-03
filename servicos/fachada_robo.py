import os
from nucleo.postagem import Postagem
from repositorios.repositorio_json import RepositorioJSON
from servicos.servico_gemini import ServicoGemini
from servicos.agendador_postagem import AgendadorPostagem
from automacao.conexao_chrome import ConexaoChrome
from automacao.automacao_instagram import AutomacaoInstagram

class FachadaRobo:
    """
    Responsabilidade: Fachada unificada que expõe serviços do robô para a camada de apresentação.
    Camada: servicos (Facade Pattern)
    """
    def __init__(self, repositorio=None, ia=None):
        self.repositorio = repositorio or RepositorioJSON()
        self.ia = ia or ServicoGemini()
        # Garante que o agendador em background está ativo
        self.agendador = AgendadorPostagem(self.repositorio)
        self.agendador.iniciar()

    def planejar_e_adicionar_postagem(self, caminhos_midias: list, prompt_contexto: str) -> Postagem:
        """Usa a IA para criar o post (legenda + horário) e o adiciona à fila local."""
        from PIL import Image as PILImage
        img_analise = PILImage.open(caminhos_midias[0])
        
        resultado_ia = self.ia.gerar_legenda_e_horario(img_analise, prompt_contexto)
        
        post = Postagem(
            id_post=0,
            caminhos_midias=caminhos_midias,
            legenda=resultado_ia["legenda"],
            horario_sugerido=resultado_ia["horario"]
        )
        self.repositorio.salvar(post)
        return post

    def agendar_postagem(self, id_post: int, data_hora: str) -> None:
        """Muda o status do post para agendado no horário desejado."""
        post = self.repositorio.obter_por_id(id_post)
        post.data_hora_agendamento = data_hora
        post.status = "Agendado"
        self.repositorio.salvar(post)

    def obter_postagens_fila(self) -> list[Postagem]:
        """Obtém todas as postagens planejadas na fila."""
        return self.repositorio.obter_todos()

    def remover_postagem(self, id_post: int) -> None:
        """Remove a postagem da fila de dados."""
        self.repositorio.remover(id_post)

    def publicar_postagem_agora(self, id_post: int) -> str:
        """Aciona o robô no Chrome para publicar a postagem imediatamente."""
        post = self.repositorio.obter_por_id(id_post)
        
        conexao = ConexaoChrome()
        automacao = AutomacaoInstagram(conexao)
        resultado = automacao.publicar_post_instagram(post.caminhos_midias, post.legenda)
        
        post.status = "Postado"
        self.repositorio.salvar(post)
        return resultado

    def capturar_postagem_chrome(self) -> dict:
        """Captura o texto selecionado e a tela do Instagram ativa no Chrome."""
        conexao = ConexaoChrome()
        automacao = AutomacaoInstagram(conexao)
        return automacao.capturar_post_e_tela()

    def gerar_comentario_contextual(self, texto_post: str) -> str:
        """Gera um comentário inteligente usando o print do Chrome se disponível."""
        caminho_print = os.path.join("outputs", "instagram_capture.png")
        return self.ia.gerar_comentario_contextual(texto_post, caminho_print)

    def postar_comentario_chrome(self, texto_comentario: str) -> str:
        """Publica o comentário gerado na aba ativa do Chrome."""
        conexao = ConexaoChrome()
        automacao = AutomacaoInstagram(conexao)
        return automacao.enviar_comentario(texto_comentario)

    def pesquisar_hashtags(self, tema: str, quantidade: int) -> str:
        """Pesquisa as hashtags que mais engajam para o tema sugerido."""
        return self.ia.gerar_hashtags_estrategicas(tema, quantidade)
