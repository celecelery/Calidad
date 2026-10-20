import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture
def usuario(db):
    return get_user_model().objects.create_user(
        username="ana", password="clave-segura-123"
    )


def test_sin_sesion_redirige_al_login(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 302
    assert respuesta.url.startswith(reverse("login"))


def test_login_con_credenciales_correctas(client, usuario):
    respuesta = client.post(
        reverse("login"), {"username": "ana", "password": "clave-segura-123"}
    )
    assert respuesta.status_code == 302
    assert client.get("/").status_code == 200


def test_login_con_credenciales_incorrectas(client, usuario):
    respuesta = client.post(
        reverse("login"), {"username": "ana", "password": "mala"}
    )
    assert respuesta.status_code == 200
    assert "incorrectos" in respuesta.content.decode()


def test_logout_cierra_la_sesion(client, usuario):
    client.force_login(usuario)
    respuesta = client.post(reverse("logout"))
    assert respuesta.status_code == 302
    assert client.get("/").status_code == 302


def test_contrasena_guardada_con_hash(usuario):
    assert usuario.password != "clave-segura-123"
    assert usuario.check_password("clave-segura-123")
