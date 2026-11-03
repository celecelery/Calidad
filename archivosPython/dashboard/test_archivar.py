"""Pruebas de RF-05: archivar un proyecto sin borrarlo (y reactivarlo)."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .models import Corte, Metrica, MetricaProyecto, Periodo, Proyecto, Usuario


class ArchivarBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="angel", password="clave-segura-123"
        )
        # Perfil de administrador ligado al usuario que inicia sesión en las pruebas.
        cls.admin = Usuario.objects.create(
            nombre="Admin de pruebas", perfil="administrador", user=cls.usuario
        )
        cls.lider = Usuario.objects.create(nombre="Angel Mazón", perfil="Administrador")
        cls.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )

    def setUp(self):
        self.client.force_login(self.usuario)
        self.proyecto = self.crear_proyecto("Dashboard SQA")

    def crear_proyecto(self, nombre):
        return Proyecto.objects.create(
            nombre=nombre,
            descripcion="Proyecto de prueba",
            integrantes=4,
            lider=self.lider,
            periodo=self.periodo,
        )

    def archivar(self, proyecto=None):
        proyecto = proyecto or self.proyecto
        return self.client.post(reverse("archivar_proyecto", args=[proyecto.pk]))

    def reactivar(self, proyecto=None):
        proyecto = proyecto or self.proyecto
        return self.client.post(reverse("reactivar_proyecto", args=[proyecto.pk]))

    def mensajes(self, respuesta):
        return [str(m) for m in get_messages(respuesta.wsgi_request)]


class ModeloArchivarTests(ArchivarBase):
    def test_archivar_cambia_el_estado(self):
        self.proyecto.archivar()
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.estado, Proyecto.Estado.ARCHIVADO)
        self.assertTrue(self.proyecto.archivado)

    def test_reactivar_vuelve_a_activo(self):
        self.proyecto.archivar()
        self.proyecto.reactivar()
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.estado, Proyecto.Estado.ACTIVO)
        self.assertFalse(self.proyecto.archivado)

    def test_archivar_no_reasigna_metricas_quitadas(self):
        # archivar() guarda solo el estado: no toca las métricas del proyecto (RF-07).
        self.proyecto.metricas.remove(Metrica.objects.get(clave="M-06"))
        self.proyecto.archivar()
        self.assertFalse(self.proyecto.metricas.filter(clave="M-06").exists())


class VistaArchivarTests(ArchivarBase):
    def test_archivar_no_borra_el_proyecto_ni_sus_datos(self):
        corte = Corte.objects.create(proyecto=self.proyecto, fecha=date(2026, 10, 20))
        MetricaProyecto.objects.create(
            proyecto=self.proyecto,
            metrica=Metrica.objects.get(clave="M-01"),
            corte=corte,
            valor=Decimal("72"),
        )
        respuesta = self.archivar()
        self.assertRedirects(respuesta, reverse("lista_proyectos"))
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.estado, "Archivado")
        self.assertEqual(self.proyecto.cortes.count(), 1)
        self.assertEqual(MetricaProyecto.objects.filter(proyecto=self.proyecto).count(), 1)
        self.assertEqual(self.proyecto.metricas.count(), 6)

    def test_mensaje_de_confirmacion(self):
        respuesta = self.archivar()
        self.assertIn(
            "Proyecto «Dashboard SQA» archivado. Sus mediciones, técnicas y reportes se conservan.",
            self.mensajes(respuesta),
        )

    def test_solo_se_archiva_ese_proyecto(self):
        otro = self.crear_proyecto("App de inventario")
        self.archivar()
        otro.refresh_from_db()
        self.assertEqual(otro.estado, "Activo")

    def test_archivado_sale_del_menu_lateral(self):
        url = reverse("metricas_proyecto", args=[self.proyecto.pk])
        enlace = f'class="tree" href="{url}"'
        self.assertContains(self.client.get(reverse("lista_metricas")), enlace)
        self.archivar()
        self.assertNotContains(self.client.get(reverse("lista_metricas")), enlace)

    def test_archivado_sigue_en_la_lista_y_en_el_filtro_por_estado(self):
        self.archivar()
        respuesta = self.client.get(reverse("lista_proyectos"), {"estado": "Archivado"})
        self.assertEqual(list(respuesta.context["proyectos"]), [self.proyecto])
        self.assertContains(respuesta, '<tr class="archived">', html=False)

    def test_archivar_dos_veces_avisa_que_ya_estaba_archivado(self):
        self.archivar()
        respuesta = self.archivar()
        self.assertIn("El proyecto «Dashboard SQA» ya estaba archivado.", self.mensajes(respuesta))

    def test_archivar_solo_acepta_post(self):
        respuesta = self.client.get(reverse("archivar_proyecto", args=[self.proyecto.pk]))
        self.assertEqual(respuesta.status_code, 405)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.estado, "Activo")

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.post(reverse("archivar_proyecto", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.archivar()
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.estado, "Activo")


class VistaReactivarTests(ArchivarBase):
    def test_reactivar_lo_devuelve_al_menu(self):
        self.archivar()
        respuesta = self.reactivar()
        self.assertRedirects(respuesta, reverse("lista_proyectos"))
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.estado, "Activo")
        self.assertIn("Proyecto «Dashboard SQA» reactivado.", self.mensajes(respuesta))
        url = reverse("metricas_proyecto", args=[self.proyecto.pk])
        enlace = f'class="tree" href="{url}"'
        self.assertContains(self.client.get(reverse("lista_metricas")), enlace)

    def test_reactivar_un_activo_avisa(self):
        respuesta = self.reactivar()
        self.assertIn("El proyecto «Dashboard SQA» ya estaba activo.", self.mensajes(respuesta))

    def test_reactivar_solo_acepta_post(self):
        respuesta = self.client.get(reverse("reactivar_proyecto", args=[self.proyecto.pk]))
        self.assertEqual(respuesta.status_code, 405)


class PantallasArchivarTests(ArchivarBase):
    def test_datos_del_proyecto_muestra_la_tarjeta_de_archivar(self):
        respuesta = self.client.get(reverse("editar_proyecto", args=[self.proyecto.pk]))
        self.assertContains(respuesta, reverse("archivar_proyecto", args=[self.proyecto.pk]))
        self.assertContains(respuesta, "<b>no se borra</b>", html=False)
        self.assertEqual(respuesta.context["resumen"], {"cortes": 0, "metricas": 6, "tecnicas": 0})

    def test_datos_de_un_archivado_ofrece_reactivar(self):
        self.archivar()
        respuesta = self.client.get(reverse("editar_proyecto", args=[self.proyecto.pk]))
        self.assertContains(respuesta, reverse("reactivar_proyecto", args=[self.proyecto.pk]))
        self.assertNotContains(respuesta, reverse("archivar_proyecto", args=[self.proyecto.pk]))

    def test_lista_ofrece_reactivar_solo_a_los_archivados(self):
        otro = self.crear_proyecto("App de inventario")
        self.archivar()
        respuesta = self.client.get(reverse("lista_proyectos"))
        self.assertContains(respuesta, reverse("reactivar_proyecto", args=[self.proyecto.pk]))
        self.assertNotContains(respuesta, reverse("reactivar_proyecto", args=[otro.pk]))