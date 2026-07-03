from abc import ABC, abstractmethod
from nucleo.postagem import Postagem

class BaseRepositorio(ABC):
    """
    Responsabilidade: Definir a interface abstrata para persistência de Postagens.
    Camada: repositorios (Gateway Interface)
    """
    @abstractmethod
    def salvar(self, postagem: Postagem) -> None:
        pass

    @abstractmethod
    def obter_todos(self) -> list[Postagem]:
        pass

    @abstractmethod
    def obter_por_id(self, id_post: int) -> Postagem:
        pass

    @abstractmethod
    def remover(self, id_post: int) -> None:
        pass
