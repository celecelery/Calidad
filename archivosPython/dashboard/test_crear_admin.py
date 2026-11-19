import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from dashboard.models import Usuario


@pytest.mark.django_db
def test_crear_admin_sin_variables_no_hace_nada(monkeypatch):
    monkeypatch.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
    call_command("crear_admin")
    assert get_user_model().objects.count() == 0


@pytest.mark.django_db
def test_crear_admin_crea_usuario_con_perfil(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "clave-de-prueba-123")
    call_command("crear_admin")
    call_command("crear_admin")
    user = get_user_model().objects.get(username="admin")
    assert user.is_superuser and user.check_password("clave-de-prueba-123")
    assert Usuario.objects.get(user=user).perfil == "administrador"
