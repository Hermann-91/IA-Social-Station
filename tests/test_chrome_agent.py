import pytest
from unittest.mock import MagicMock
from chrome_agent import DepuradorChrome, AutomatizadorInstagram

def test_depurador_chrome_obter_abas_sucesso(mocker):
    depurador = DepuradorChrome()
    
    # Simula a resposta HTTP de listagem de abas do Chrome
    mock_response = MagicMock()
    mock_response.read.return_value = b'[{"type": "page", "title": "Instagram", "url": "https://instagram.com", "webSocketDebuggerUrl": "ws://local"}]'
    mocker.patch("urllib.request.urlopen", return_value=mock_response)

    abas = depurador.obter_abas()
    
    assert len(abas) == 1
    assert abas[0]["title"] == "Instagram"


def test_automatizador_instagram_capturar_post_sucesso(mocker):
    mock_depurador = MagicMock()
    mock_depurador.obter_abas.return_value = [
        {"type": "page", "title": "Instagram", "url": "https://instagram.com/p/123", "webSocketDebuggerUrl": "ws://local"}
    ]
    
    # Simula as respostas do protocolo CDP do Chrome (Texto Selecionado, Ativação de Página, Screenshot)
    mock_depurador.enviar_comando.side_effect = [
        {"result": {"result": {"value": "Texto Selecionado Teste"}}}, # Resposta do Runtime.evaluate
        {}, # Resposta do Page.enable
        {"result": {"data": "dGVzdGU="}} # Base64 para dados da imagem
    ]

    automatizador = AutomatizadorInstagram(mock_depurador)
    
    # Mocks para impedir gravação real de arquivos em disco durante os testes
    mocker.patch("os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    resultado = automatizador.capturar_post_e_tela(diretorio_saida="/tmp")

    assert resultado["texto_selecionado"] == "Texto Selecionado Teste"
    assert resultado["url"] == "https://instagram.com/p/123"
    mock_depurador.conectar_aba.assert_called_once_with("ws://local")
    mock_depurador.fechar.assert_called_once()
