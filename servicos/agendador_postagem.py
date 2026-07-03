import threading
import time
import os
from datetime import datetime
from repositorios.repositorio_json import RepositorioJSON
from automacao.conexao_chrome import ConexaoChrome
from automacao.automacao_instagram import AutomacaoInstagram

class AgendadorPostagem:
    """
    Responsabilidade: Monitorar e executar postagens agendadas em segundo plano.
    Camada: servicos (Application Service / Singleton)
    """
    _instancia = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instancia:
                cls._instancia = super().__new__(cls)
                cls._instancia._iniciado = False
            return cls._instancia

    def __init__(self, repositorio=None):
        if self._iniciado:
            return
        self.repositorio = repositorio or RepositorioJSON()
        self.rodando = False
        self._iniciado = True

    def iniciar(self) -> None:
        """Inicia a thread em segundo plano se ela já não estiver ativa."""
        if self.rodando:
            return
        self.rodando = True
        self.thread = threading.Thread(target=self._loop_monitoramento, daemon=True)
        self.thread.start()
        print("AgendadorPostagem: Monitorador iniciado em segundo plano.")

    def _loop_monitoramento(self) -> None:
        while self.rodando:
            try:
                postagens = self.repositorio.obter_todos()
                agora = datetime.now()
                alterado = False

                for post in postagens:
                    if post.status == "Agendado" and post.data_hora_agendamento:
                        dt_agendado = datetime.strptime(post.data_hora_agendamento, "%Y-%m-%d %H:%M:%S")
                        
                        if agora >= dt_agendado:
                            post.status = "Postando automaticamente..."
                            self.repositorio.salvar(post)
                            
                            try:
                                conexao = ConexaoChrome()
                                automacao = AutomacaoInstagram(conexao)
                                res = automacao.publicar_post_instagram(post.caminhos_midias, post.legenda)
                                post.status = f"Postado automaticamente às {agora.strftime('%H:%M')}"
                            except Exception as e:
                                post.status = f"Falha no agendamento: {str(e)}"
                            
                            self.repositorio.salvar(post)
                            alterado = True
            except Exception as e:
                print(f"Erro no loop do AgendadorPostagem: {e}")
                
            time.sleep(30)
