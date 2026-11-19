"""Crea el primer Administrador a partir de variables de entorno.

Se usa en el despliegue en la nube, donde no hay consola interactiva.
Si DJANGO_SUPERUSER_USERNAME o DJANGO_SUPERUSER_PASSWORD no están definidas,
no hace nada. Si el usuario ya existe, solo se asegura de que tenga perfil.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from dashboard.models import Usuario


class Command(BaseCommand):
    help = "Crea el superusuario inicial con perfil de Administrador desde variables de entorno."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not username or not password:
            self.stdout.write("crear_admin: variables no definidas, se omite.")
            return
        User = get_user_model()
        user, creado = User.objects.get_or_create(
            username=username,
            defaults={
                "email": os.getenv("DJANGO_SUPERUSER_EMAIL", ""),
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if creado:
            user.set_password(password)
            user.save()
        Usuario.objects.update_or_create(
            user=user,
            defaults={
                "nombre": os.getenv("DJANGO_SUPERUSER_NOMBRE", username),
                "perfil": "administrador",
            },
        )
        self.stdout.write(f"crear_admin: listo ({'creado' if creado else 'ya existía'}).")
