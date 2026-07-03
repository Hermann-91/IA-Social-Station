import base64
import os
import time
import json
from automacao.conexao_chrome import ConexaoChrome
from automacao.base_automacao import BaseAutomacao

class AutomacaoInstagram(BaseAutomacao):
    """
    Responsabilidade: Lógica de automação específica das páginas do Instagram.
    Camada: automacao (Device Automation Implementation)
    """
    def _localizar_aba_instagram(self) -> dict:
        """Procura e seleciona a aba ativa que contém a URL do Instagram."""
        abas = self.conexao.obter_abas()
        
        for aba in abas:
            if aba.get("type") == "page" and "instagram.com" in aba.get("url", ""):
                return aba
                
        for aba in abas:
            if aba.get("type") == "page":
                return aba
                
        raise ValueError("Nenhuma aba ativa do navegador foi encontrada.")

    def capturar_post_e_tela(self, diretorio_saida="outputs") -> dict:
        """Lê o texto selecionado, o título, a URL e captura um print de tela da aba ativa."""
        aba = self._localizar_aba_instagram()
        self.conexao.conectar_aba(aba["webSocketDebuggerUrl"])
        
        try:
            res_texto = self.conexao.enviar_comando(
                "Runtime.evaluate",
                {"expression": "window.getSelection().toString()", "returnByValue": True}
            )
            texto_selecionado = ""
            if "result" in res_texto and "result" in res_texto["result"]:
                texto_selecionado = res_texto["result"]["result"].get("value", "")

            self.conexao.enviar_comando("Page.enable")
            res_print = self.conexao.enviar_comando("Page.captureScreenshot", {"format": "png"})
            
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
            self.conexao.fechar()

    def enviar_comentario(self, texto_comentario: str) -> str:
        """Injeta a automação JS para preencher e enviar o comentário na aba ativa do Instagram."""
        aba = self._localizar_aba_instagram()
        self.conexao.conectar_aba(aba["webSocketDebuggerUrl"])
        
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
            res = self.conexao.enviar_comando("Runtime.evaluate", {"expression": js_code, "returnByValue": True})
            resultado = ""
            if "result" in res and "result" in res["result"]:
                resultado = res["result"]["result"].get("value", "")
            if "Erro" in resultado:
                raise ValueError(resultado)
            return resultado
        finally:
            self.conexao.fechar()

    def publicar_post_instagram(self, caminhos_arquivos: list, texto_legenda: str) -> str:
        """Automatiza o fluxo de publicação (criação, upload, legenda e envio)."""
        aba = self._localizar_aba_instagram()
        self.conexao.conectar_aba(aba["webSocketDebuggerUrl"])
        
        try:
            # Passo 1: Abre o modal de criação
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
            res_abrir = self.conexao.enviar_comando("Runtime.evaluate", {"expression": js_abrir_modal, "returnByValue": True})
            status_abrir = res_abrir["result"]["result"].get("value", "")
            if "Erro" in status_abrir:
                raise ValueError(status_abrir)
            
            time.sleep(2.0)
            
            # Passo 2: Localiza o input e faz o upload
            res_eval = self.conexao.enviar_comando(
                "Runtime.evaluate", 
                {"expression": "document.querySelector(\"input[type='file']\")", "includeCommandLineAPI": True}
            )
            
            if "result" not in res_eval or "result" not in res_eval["result"] or "objectId" not in res_eval["result"]["result"]:
                raise ValueError("Erro: Input de upload de arquivos do Instagram não encontrado no modal. O modal chegou a abrir?")
                
            object_id = res_eval["result"]["result"]["objectId"]
            
            self.conexao.enviar_comando("DOM.enable")
            self.conexao.enviar_comando("DOM.getDocument", {"depth": -1, "pierce": True})
            res_node = self.conexao.enviar_comando("DOM.requestNode", {"objectId": object_id})
            
            if "result" not in res_node or "nodeId" not in res_node["result"]:
                raise ValueError("Erro ao mapear o elemento de upload de arquivos no protocolo do Chrome.")
                
            input_node_id = res_node["result"]["nodeId"]
            self.conexao.enviar_comando("DOM.setFileInputFiles", {"nodeId": input_node_id, "files": caminhos_arquivos})
            
            time.sleep(3.0)
            
            # Passo 3 e 4: Avançar telas
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
                return "Erro: Botão Avançar não encontrado.";
            })();
            """
            self.conexao.enviar_comando("Runtime.evaluate", {"expression": js_avancar})
            time.sleep(1.5)
            self.conexao.enviar_comando("Runtime.evaluate", {"expression": js_avancar})
            time.sleep(1.5)
            
            # Passo 5: Insere a legenda
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
            self.conexao.enviar_comando("Runtime.evaluate", {"expression": js_escrever_legenda})
            time.sleep(1.5)
            
            # Passo 6: Publicar
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
            res_final = self.conexao.enviar_comando("Runtime.evaluate", {"expression": js_compartilhar, "returnByValue": True})
            return res_final["result"]["result"].get("value", "")
            
        except Exception as e:
            try:
                self.conexao.enviar_comando("Page.enable")
                res_print = self.conexao.enviar_comando("Page.captureScreenshot", {"format": "png"})
                if "result" in res_print and "data" in res_print["result"]:
                    img_data = base64.b64decode(res_print["result"]["data"])
                    os.makedirs("outputs", exist_ok=True)
                    with open("outputs/error_screenshot.png", "wb") as f:
                        f.write(img_data)
            except Exception as print_err:
                print(f"Erro ao capturar screenshot de erro: {print_err}")
            raise e
        finally:
            self.conexao.fechar()
