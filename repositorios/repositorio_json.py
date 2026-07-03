import json
import os
from nucleo.postagem import Postagem
from repositorios.base_repositorio import BaseRepositorio

class RepositorioJSON(BaseRepositorio):
    """
    Responsabilidade: Implementar a persistência de postagens em formato de arquivo JSON local.
    Camada: repositorios (Gateway Implementation)
    """
    def __init__(self, caminho_arquivo: str = None):
        self.caminho_arquivo = caminho_arquivo or os.path.join("outputs", "fila_postagens.json")
        os.makedirs(os.path.dirname(self.caminho_arquivo), exist_ok=True)

    def _ler_arquivo(self) -> list:
        if not os.path.exists(self.caminho_arquivo):
            return []
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _salvar_arquivo(self, dados: list) -> None:
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def obter_todos(self) -> list[Postagem]:
        dados_brutos = self._ler_arquivo()
        return [Postagem.criar_de_dicionario(d) for d in dados_brutos]

    def obter_por_id(self, id_post: int) -> Postagem:
        todos = self.obter_todos()
        for p in todos:
            if p.id == id_post:
                return p
        raise ValueError(f"Postagem com ID {id_post} não encontrada.")

    def salvar(self, postagem: Postagem) -> None:
        todos = self.obter_todos()
        post_existente_idx = -1
        
        for idx, p in enumerate(todos):
            if p.id == postagem.id:
                post_existente_idx = idx
                break
                
        if post_existente_idx != -1:
            todos[post_existente_idx] = postagem
        else:
            # Garante ID autoincremento se for um post novo
            if not postagem.id:
                postagem.id = max([p.id for p in todos], default=0) + 1
            todos.append(postagem)
            
        dados_json = [p.converter_para_dicionario() for p in todos]
        self._salvar_arquivo(dados_json)

    def remover(self, id_post: int) -> None:
        todos = self.obter_todos()
        filtrados = [p for p in todos if p.id != id_post]
        dados_json = [p.converter_para_dicionario() for p in filtrados]
        self._salvar_arquivo(dados_json)
