import sys
import json
import urllib.request
import base64
import os
from websocket import create_connection

class DepuradorChrome:
    """
    Responsabilidade: Gerenciar a conexão de rede de depuração remota com o Chrome (CDP).
    Princípio: SRP (Single Responsibility Principle) - Foca apenas em rede e transporte de comandos.
    """
    def __init__(self, host="localhost", port=9222):
        self.base_url = f"http://{host}:{port}"
        self.ws = None

    def obter_abas(self):
        """Busca todas as abas abertas no navegador de depuração."""
        try:
            req = urllib.request.urlopen(f"{self.base_url}/json")
            return json.loads(req.read().decode())
        except Exception as e:
            raise ConnectionError(
                f"Chrome não detectado na porta de depuração. Certifique-se de que ele foi aberto. Detalhes: {e}"
            )

    def conectar_aba(self, ws_url):
        """Estabelece a conexão WebSocket com uma aba específica."""
        self.ws = create_connection(ws_url)

    def fechar(self):
        """Encerra a conexão WebSocket ativa."""
        if self.ws:
            self.ws.close()
            self.ws = None

    def enviar_comando(self, method, params=None):
        """Envia um comando do protocolo Chrome DevTools (CDP) e retorna a resposta."""
        if not self.ws:
            raise ConnectionError("Nenhuma conexão WebSocket ativa com o navegador.")
            
        cmd = {
            "id": 1,
            "method": method,
            "params": params or {}
        }
        self.ws.send(json.dumps(cmd))
        return json.loads(self.ws.recv())


class AutomatizadorInstagram:
    """
    Responsabilidade: Lógica de automação específica das páginas do Instagram.
    Princípio: SRP - Lida unicamente com a interface e elementos do Instagram.
    """
    def __init__(self, depurador: DepuradorChrome):
        self.depurador = depurador

    def _localizar_aba_instagram(self) -> dict:
        """Procura e seleciona a aba ativa que contém a URL do Instagram."""
        abas = self.depurador.obter_abas()
        
        # Tenta achar a aba do Instagram
        for aba in abas:
            if aba.get("type") == "page" and "instagram.com" in aba.get("url", ""):
                return aba
                
        # Fallback para qualquer aba de página comum se não achar Instagram
        for aba in abas:
            if aba.get("type") == "page":
                return aba
                
        raise ValueError("Nenhuma aba ativa do navegador foi encontrada.")

    def capturar_post_e_tela(self, diretorio_saida="outputs") -> dict:
        """Lê o texto selecionado, o título, a URL e captura um print de tela da aba ativa."""
        aba = self._localizar_aba_instagram()
        self.depurador.conectar_aba(aba["webSocketDebuggerUrl"])
        
        try:
            # 1. Executa JS para obter a seleção de texto na página
            res_texto = self.depurador.enviar_comando(
                "Runtime.evaluate",
                {"expression": "window.getSelection().toString()", "returnByValue": True}
            )
            texto_selecionado = ""
            if "result" in res_texto and "result" in res_texto["result"]:
                texto_selecionado = res_texto["result"]["result"].get("value", "")

            # 2. Habilita as APIs de página e captura a imagem da tela (Screenshot)
            self.depurador.enviar_comando("Page.enable")
            res_print = self.depurador.enviar_comando("Page.captureScreenshot", {"format": "png"})
            
            caminho_print = None
            if "result" in res_print and "data" in res_print["result"]:
                img_data = base64.b64decode(res_print["result"]["data"])
                
                os.makedirs(diretorio_saida, exist_ok=True)
                caminho_print = os.path.join(diretorio_saida, "instagram_capture.png")
                with open(caminho_print, "wb") as f:
                    f.write(img_data)
                    
            return {
                "titulo": aba.get("title", ""),
                "url": aba.get("url", ""),
                "texto_selecionado": texto_selecionado,
                "caminho_screenshot": caminho_print
            }
            
        finally:
            self.depurador.fechar()

    def enviar_comentario(self, texto_comentario: str) -> str:
        """Injeta a automação JS para preencher e enviar o comentário na aba ativa do Instagram."""
        aba = self._localizar_aba_instagram()
        self.depurador.conectar_aba(aba["webSocketDebuggerUrl"])
        
        # JavaScript estruturado para interagir com o DOM do Instagram
        js_code = f"""
        (() => {{
            const textarea = document.querySelector('form textarea') || 
                             document.querySelector('textarea[placeholder*="comentário"]') || 
                             document.querySelector('textarea[placeholder*="comment"]') ||
                             document.querySelector('textarea');
                             
            if (!textarea) {{
                return "Erro: Campo de comentário não encontrado.";
            }}
            
            textarea.focus();
            textarea.select();
            
            // Simula a digitação física para atualizar o estado do React
            document.execCommand('insertText', false, {json.dumps(texto_comentario)});
            
            textarea.dispatchEvent(new Event('focus', {{ bubbles: true }}));
            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
            
            let submitBtn = null;
            const buttons = Array.from(document.querySelectorAll('form button, [role="button"], button'));
            
            submitBtn = buttons.find(btn => {{
                const txt = btn.textContent.trim();
                return txt === 'Postar' || txt === 'Post' || txt === 'Publicar';
            }});
            
            if (!submitBtn) {{
                submitBtn = buttons.find(btn => 
                    btn.textContent.includes('Postar') || 
                    btn.textContent.includes('Post')
                );
            }}
            
            if (!submitBtn) {{
                return "Erro: Botão de envio não encontrado.";
            }}
            
            setTimeout(() => {{
                submitBtn.disabled = false;
                submitBtn.click();
                
                const form = textarea.closest('form');
                if (form) {{
                    form.dispatchEvent(new Event('submit', {{ bubbles: true, cancelable: true }}));
                }}
            }}, 300);
            
            return "Comentário preenchido e comando de envio disparado.";
        }})();
        """
        
        try:
            res = self.depurador.enviar_comando("Runtime.evaluate", {"expression": js_code, "returnByValue": True})
            
            resultado = ""
            if "result" in res and "result" in res["result"]:
                resultado = res["result"]["result"].get("value", "")
                
            if "Erro" in resultado:
                raise ValueError(resultado)
                
            return resultado
        finally:
            self.depurador.fechar()
