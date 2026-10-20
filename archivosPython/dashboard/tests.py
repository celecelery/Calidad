from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

RUTAS_DASH = (
    "/django_plotly_dash/app/MiDashboard/",
    "/django_plotly_dash/app/MiDashboard/_dash-layout",
)


class InicioTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="ana", password="clave-segura-123"
        )

    def test_pagina_dash_carga_con_sesion(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 200)

    def test_pagina_dash_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.url.startswith(reverse("login")))

    def test_pantallas_dash_sin_sesion_redirigen_al_login(self):
        for ruta in RUTAS_DASH:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 302)
                self.assertTrue(respuesta.url.startswith(reverse("login")))

    def test_app_dash_carga_con_sesion(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(RUTAS_DASH[0])
        self.assertEqual(respuesta.status_code, 200)

    def test_inicio_muestra_boton_cerrar_sesion(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, 'action="/logout/"')