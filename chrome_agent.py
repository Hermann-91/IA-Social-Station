import sys
import json
import urllib.request
import base64
import os
import time
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

    def publicar_post_instagram(self, caminhos_arquivos: list, texto_legenda: str) -> str:
        """
        Automatiza o fluxo completo de publicação no Instagram:
        Abre o modal de criação, faz o upload dos arquivos via CDP, insere a legenda e publica.
        """
        aba = self._localizar_aba_instagram()
        self.depurador.conectar_aba(aba["webSocketDebuggerUrl"])
        
        try:
            # Passo 1: Injeta JS para clicar no botão "Criar" (Nova Publicação) na barra lateral
            js_abrir_modal = """
            (() => {
                let criarBtn = document.querySelector('a[href*="/create/"]') || 
                               document.querySelector('a[href*="/create/select/"]') ||
                               document.querySelector('a[href*="create"]') ||
                               Array.from(document.querySelectorAll('svg, span')).find(el => {
                                   const label = el.getAttribute('aria-label') || el.textContent || '';
                                   return label.includes('Nova publicação') || label.includes('Criar') || label.includes('Create');
                               });
                if (criarBtn) {
                    const clicavel = criarBtn.closest('a') || criarBtn.closest('button') || criarBtn;
                    clicavel.click();
                    clicavel.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return "Botão Criar clicado.";
                }
                return "Erro: Botão Criar não encontrado na interface.";
            })();
            """
            res_abrir = self.depurador.enviar_comando("Runtime.evaluate", {"expression": js_abrir_modal, "returnByValue": True})
            status_abrir = res_abrir["result"]["result"].get("value", "")
            if "Erro" in status_abrir:
                raise ValueError(status_abrir)
            
            # Aguarda 2 segundos para o modal de criação do Instagram carregar no DOM
            time.sleep(2.0)
            
            # Passo 2: Localiza o input de arquivo via CDP e faz o upload dos caminhos físicos
            res_eval = self.depurador.enviar_comando(
                "Runtime.evaluate", 
                {"expression": "document.querySelector(\"input[type='file']\")", "includeCommandLineAPI": True}
            )
            
            if "result" not in res_eval or "result" not in res_eval["result"] or "objectId" not in res_eval["result"]["result"]:
                raise ValueError("Erro: Input de upload de arquivos do Instagram não encontrado no modal. O modal chegou a abrir?")
                
            object_id = res_eval["result"]["result"]["objectId"]
            
            # Converte o objectId do JS para o nodeId do DOM do CDP
            self.depurador.enviar_comando("DOM.enable")
            self.depurador.enviar_comando("DOM.getDocument", {"depth": -1, "pierce": True})
            res_node = self.depurador.enviar_comando("DOM.requestNode", {"objectId": object_id})
            
            if "result" not in res_node or "nodeId" not in res_node["result"]:
                raise ValueError("Erro ao mapear o elemento de upload de arquivos no protocolo do Chrome.")
                
            input_node_id = res_node["result"]["nodeId"]
            
            # Injeta os arquivos no Chrome de forma transparente (sem abrir a janela do sistema)
            self.depurador.enviar_comando(
                "DOM.setFileInputFiles", 
                {"nodeId": input_node_id, "files": caminhos_arquivos}
            )
            
            # Aguarda 3 segundos para o Chrome renderizar as fotos e carregar
            time.sleep(3.0)
            
            # Passo 3: Clique no primeiro "Avançar" (Corte/Aspecto)
            js_avancar = """
            (() => {
                const avancarBtn = Array.from(document.querySelectorAll('[role="button"], button')).find(el => {
                    const text = el.textContent.trim();
                    return text === 'Avançar' || text === 'Next';
                });
                if (avancarBtn) {
                    avancarBtn.click();
                    return "Avançar clicado.";
                }
                return "Erro: Botão Avançar não encontrado na tela de corte.";
            })();
            """
            self.depurador.enviar_comando("Runtime.evaluate", {"expression": js_avancar})
            time.sleep(1.5)
            
            # Passo 4: Clique no segundo "Avançar" (Filtros/Edição)
            self.depurador.enviar_comando("Runtime.evaluate", {"expression": js_avancar})
            time.sleep(1.5)
            
            # Passo 5: Preenche o campo de Legenda do Post
            js_escrever_legenda = f"""
            (() => {{
                const legendaBox = document.querySelector('[aria-label="Escreva uma legenda..."]') || 
                                   document.querySelector('[aria-label="Write a caption..."]') ||
                                   document.querySelector('[role="textbox"]');
                if (!legendaBox) {{
                    return "Erro: Campo de legenda não encontrado no formulário.";
                }}
                legendaBox.focus();
                document.execCommand('insertText', false, {json.dumps(texto_legenda)});
                return "Legenda preenchida.";
            }})();
            """
            self.depurador.enviar_comando("Runtime.evaluate", {"expression": js_escrever_legenda})
            time.sleep(1.5)
            
            # Passo 6: Clique em "Compartilhar" (Publicar)
            js_compartilhar = """
            (() => {
                const compartilharBtn = Array.from(document.querySelectorAll('[role="button"], button')).find(el => {
                    const text = el.textContent.trim();
                    return text === 'Compartilhar' || text === 'Share';
                });
                if (compartilharBtn) {
                    compartilharBtn.click();
                    return "Post compartilhado com sucesso!";
                }
                return "Erro: Botão Compartilhar não encontrado.";
            })();
            """
            res_final = self.depurador.enviar_comando("Runtime.evaluate", {"expression": js_compartilhar, "returnByValue": True})
            return res_final["result"]["result"].get("value", "")
            
        except Exception as e:
            try:
                self.depurador.enviar_comando("Page.enable")
                res_print = self.depurador.enviar_comando("Page.captureScreenshot", {"format": "png"})
                if "result" in res_print and "data" in res_print["result"]:
                    img_data = base64.b64decode(res_print["result"]["data"])
                    os.makedirs("outputs", exist_ok=True)
                    with open("outputs/error_screenshot.png", "wb") as f:
                        f.write(img_data)
            except Exception as print_err:
                print(f"Erro ao capturar screenshot de erro: {print_err}")
            raise e
        finally:
            self.depurador.fechar()
