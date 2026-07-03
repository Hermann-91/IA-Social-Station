from abc import ABC, abstractmethod
from automacao.conexao_chrome import ConexaoChrome

class BaseAutomacao(ABC):
    """
    Responsabilidade: Interface abstrata que define os métodos fundamentais de automação de rede social.
    Camada: automacao (Device Interface)
    """
    def __init__(self, conexao: ConexaoChrome):
        self.conexao = conexao
