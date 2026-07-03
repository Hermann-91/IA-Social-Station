import pytest
from unittest.mock import MagicMock
from automacao.conexao_chrome import ConexaoChrome

def test_obter_abas_do_chrome(mocker):
    conexao = ConexaoChrome()
    
    mock_response = MagicMock()
    mock_response.read.return_value = b'[{"type": "page", "title": "Instagram", "url": "https://instagram.com", "webSocketDebuggerUrl": "ws://local"}]'
    mocker.patch("urllib.request.urlopen", return_value=mock_response)

    abas = conexao.obter_abas()
    assert len(abas) == 1
    assert abas[0]["title"] == "Instagram"
