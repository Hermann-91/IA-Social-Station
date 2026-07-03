import pytest
from unittest.mock import MagicMock
from servicos.fachada_robo import FachadaRobo
from nucleo.postagem import Postagem

def test_fachada_planejar_e_adicionar_postagem(mocker):
    # Mock do Gemini
    mock_ia = MagicMock()
    mock_ia.gerar_legenda_e_horario.return_value = {
        "legenda": "Legenda gerada pela IA",
        "horario": "18:00 (Pico)"
    }

    # Mock do Repositorio
    mock_repo = MagicMock()
    mock_repo.obter_todos.return_value = []

    # Mocks do Pillow
    mocker.patch("PIL.Image.open", return_value=MagicMock())

    fachada = FachadaRobo(repositorio=mock_repo, ia=mock_ia)
    
    # Executa planejamento
    post = fachada.planejar_e_adicionar_postagem(["outputs/foto.jpg"], "Falar sobre Uber")

    assert post.legenda == "Legenda gerada pela IA"
    assert post.horario_sugerido == "18:00 (Pico)"
    mock_repo.salvar.assert_called_once()
