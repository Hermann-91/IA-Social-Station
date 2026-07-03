import pytest
from unittest.mock import MagicMock
from engine import gerar_comentario_contextual, gerar_conteudo_completo, gerar_hashtags_estrategicas
from gemini_service import ServicoGemini

def test_gerar_comentario_contextual_com_sucesso(mocker):
    # 1. Cria o mock do cliente genai e da resposta de texto da IA
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Comentário teste gerado com sucesso!"
    mock_client.models.generate_content.return_value = mock_response

    # 2. Injeta o mock para evitar chamadas de rede reais
    mocker.patch("gemini_service.genai.Client", return_value=mock_client)
    mocker.patch("gemini_service.os.getenv", return_value="fake_api_key")

    resultado = gerar_comentario_contextual("Post de teste sobre custos de motorista")

    # 3. Validações
    assert resultado == "Comentário teste gerado com sucesso!"
    mock_client.models.generate_content.assert_called_once()


def test_gerar_comentario_contextual_erro_api_retorna_fallback(mocker):
    # Simula uma falha de conexão na API do Gemini
    mocker.patch("gemini_service.genai.Client", side_effect=Exception("Erro de Conexão"))
    mocker.patch("gemini_service.os.getenv", return_value="fake_api_key")

    resultado = gerar_comentario_contextual("Post de teste")

    # Garante que o sistema não quebra e retorna a mensagem amigável de fallback
    assert "Complicado, irmão!" in resultado

def test_gerar_hashtags_estrategicas_com_sucesso(mocker):
    # Mock da resposta de hashtags do Gemini
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "#nicho #publico #geral"
    mock_client.models.generate_content.return_value = mock_response

    # Injeta o mock no local de serviço correto
    mocker.patch("gemini_service.genai.Client", return_value=mock_client)
    mocker.patch("gemini_service.os.getenv", return_value="fake_api_key")

    resultado = gerar_hashtags_estrategicas("Nicho Teste", 5)

    # Validações
    assert "#nicho" in resultado
    mock_client.models.generate_content.assert_called_once()
