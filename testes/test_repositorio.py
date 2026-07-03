import os
import pytest
from nucleo.postagem import Postagem
from repositorios.repositorio_json import RepositorioJSON

def test_salvar_e_obter_postagens_no_repositorio(tmp_path):
    caminho_teste = os.path.join(tmp_path, "postagens_teste.json")
    repo = RepositorioJSON(caminho_teste)

    post = Postagem(
        id_post=1,
        caminhos_midias=["outputs/temp_0.jpg"],
        legenda="Postagem de teste",
        horario_sugerido="12:00"
    )

    repo.salvar(post)
    postagens = repo.obter_todos()

    assert len(postagens) == 1
    assert postagens[0].legenda == "Postagem de teste"
    assert postagens[0].id == 1
