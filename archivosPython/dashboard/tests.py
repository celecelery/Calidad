from django.test import TestCase
from django.urls import reverse


class InicioTests(TestCase):
    def test_pagina_dash_carga(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 200)