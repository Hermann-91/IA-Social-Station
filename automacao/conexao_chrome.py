import json
import urllib.request
from websocket import create_connection

class ConexaoChrome:
    """
    Responsabilidade: Gerenciar a conexão de rede de depuração remota com o Chrome (CDP).
    Camada: automacao (Device Connection / Driver)
    """
    def __init__(self, host="localhost", port=9222):
        self.base_url = f"http://{host}:{port}"
        self.ws = None

    def obter_abas(self) -> list:
        """Busca todas as abas abertas no navegador de depuração."""
        try:
            req = urllib.request.urlopen(f"{self.base_url}/json")
            return json.loads(req.read().decode())
        except Exception as e:
            raise ConnectionError(
                f"Chrome não detectado na porta de depuração. Certifique-se de que ele foi aberto. Detalhes: {e}"
            )

    def conectar_aba(self, ws_url: str) -> None:
        """Estabelece a conexão WebSocket com uma aba específica."""
        self.ws = create_connection(ws_url)

    def fechar(self) -> None:
        """Encerra a conexão WebSocket ativa."""
        if self.ws:
            self.ws.close()
            self.ws = None

    def enviar_comando(self, method: str, params: dict = None) -> dict:
        """Envia um comando CDP, filtra eventos assíncronos e trata erros retornados."""
        if not self.ws:
            raise ConnectionError("Nenhuma conexão WebSocket ativa com o navegador.")
            
        cmd_id = 100
        cmd = {
            "id": cmd_id,
            "method": method,
            "params": params or {}
        }
        self.ws.send(json.dumps(cmd))
        
        while True:
            res = json.loads(self.ws.recv())
            if "id" not in res:
                continue
            if res.get("id") == cmd_id:
                if "error" in res:
                    raise ValueError(f"Erro no comando CDP '{method}': {res['error'].get('message', 'Erro desconhecido')}")
                return res
