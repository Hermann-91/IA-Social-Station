from datetime import datetime

class Postagem:
    """
    Responsabilidade: Representar a entidade de negócio de uma postagem do Instagram.
    Camada: nucleo (Domain Entity)
    """
    def __init__(self, id_post: int, caminhos_midias: list, legenda: str, horario_sugerido: str, status: str = "Aguardando postagem", data_hora_agendamento: str = None):
        self.id = id_post
        self.caminhos_midias = caminhos_midias
        self.legenda = legenda
        self.horario_sugerido = horario_sugerido
        self.status = status
        self.data_hora_agendamento = data_hora_agendamento

    def converter_para_dicionario(self) -> dict:
        """Converte a entidade Postagem para um dicionário compatível com JSON."""
        return {
            "id": self.id,
            "caminhos_mídias": self.caminhos_midias,
            "legenda": self.legenda,
            "horario_sugerido": self.horario_sugerido,
            "status": self.status,
            "data_hora_agendamento": self.data_hora_agendamento
        }

    @classmethod
    def criar_de_dicionario(cls, dados: dict) -> 'Postagem':
        """Cria uma instância de Postagem a partir de um dicionário."""
        return cls(
            id_post=dados["id"],
            caminhos_midias=dados["caminhos_mídias"],
            legenda=dados["legenda"],
            horario_sugerido=dados["horario_sugerido"],
            status=dados["status"],
            data_hora_agendamento=dados.get("data_hora_agendamento")
        )
