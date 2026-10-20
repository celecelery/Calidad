"""Pruebas de RF-01 (periodo) y RF-02 (proyecto), validadas en el servidor (RNF-04)."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import PeriodoForm, ProyectoForm
from .models import Periodo, Proyecto, Usuario


class PeriodoFormTests(TestCase):
    def test_periodo_valido_se_acepta(self):
        form = PeriodoForm(
            data={"nombre": "Ago-Dic 2026", "fecha_inicio": "2026-08-10", "fecha_fin": "2026-12-15"}
        )
        self.assertTrue(form.is_valid())

    def test_fecha_fin_anterior_a_inicio_se_rechaza(self):
        form = PeriodoForm(
            data={"nombre": "Ago-Dic 2026", "fecha_inicio": "2026-12-15", "fecha_fin": "2026-08-10"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "La fecha de fin no puede ser anterior a la fecha de inicio.",
            form.errors["fecha_fin"],
        )

    def test_misma_fecha_de_inicio_y_fin_se_acepta(self):
        form = PeriodoForm(
            data={"nombre": "Un día", "fecha_inicio": "2026-10-20", "fecha_fin": "2026-10-20"}
        )
        self.assertTrue(form.is_valid())

    def test_campos_vacios_muestran_mensaje_en_espanol(self):
        form = PeriodoForm(data={})
        self.assertFalse(form.is_valid())
        for campo in ("nombre", "fecha_inicio", "fecha_fin"):
            self.assertIn("Este campo es obligatorio.", form.errors[campo])


class ProyectoFormTests(TestCase):
    def setUp(self):
        self.lider = Usuario.objects.create(nombre="Ana", perfil="Miembro")
        self.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )
        self.otro_periodo = Periodo.objects.create(
            nombre="Ene-Jun 2027", fecha_inicio=date(2027, 1, 10), fecha_fin=date(2027, 6, 15)
        )

    def datos(self, **cambios):
        datos = {
            "nombre": "Dashboard SQA",
            "descripcion": "Monitoreo de calidad",
            "lider": self.lider.pk,
            "integrantes": 4,
            "periodo": self.periodo.pk,
        }
        datos.update(cambios)
        return datos

    def crear_proyecto(self, periodo):
        return Proyecto.objects.create(
            nombre="Dashboard SQA",
            descripcion="Existente",
            integrantes=4,
            estado="Activo",
            lider=self.lider,
            periodo=periodo,
        )

    def test_proyecto_valido_se_acepta(self):
        self.assertTrue(ProyectoForm(data=self.datos()).is_valid())

    def test_sin_nombre_se_rechaza(self):
        form = ProyectoForm(data=self.datos(nombre=""))
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["nombre"])

    def test_sin_periodo_se_rechaza(self):
        form = ProyectoForm(data=self.datos(periodo=""))
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["periodo"])

    def test_nombre_repetido_en_el_mismo_periodo_se_rechaza(self):
        self.crear_proyecto(self.periodo)
        form = ProyectoForm(data=self.datos(nombre="dashboard sqa"))
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ya existe un proyecto con ese nombre en el periodo seleccionado.",
            form.errors["nombre"],
        )

    def test_mismo_nombre_en_otro_periodo_se_acepta(self):
        self.crear_proyecto(self.otro_periodo)
        self.assertTrue(ProyectoForm(data=self.datos()).is_valid())

    def test_editar_proyecto_sin_cambiar_nombre_se_acepta(self):
        proyecto = self.crear_proyecto(self.periodo)
        form = ProyectoForm(data=self.datos(descripcion="Nueva"), instance=proyecto)
        self.assertTrue(form.is_valid())

    def test_integrantes_menor_a_uno_se_rechaza(self):
        form = ProyectoForm(data=self.datos(integrantes=0))
        self.assertFalse(form.is_valid())
        self.assertIn("El proyecto debe tener al menos 1 integrante.", form.errors["integrantes"])

    def test_lider_inexistente_se_rechaza(self):
        form = ProyectoForm(data=self.datos(lider=9999))
        self.assertFalse(form.is_valid())
        self.assertIn("Selecciona un líder de la lista.", form.errors["lider"])


class VistasFormulariosTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="ana", password="clave-segura-123"
        )
        self.client.force_login(self.usuario)
        self.lider = Usuario.objects.create(nombre="Ana", perfil="Miembro")
        self.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )

    def test_formularios_cargan(self):
        for nombre in ("periodo_nuevo", "proyecto_nuevo"):
            with self.subTest(vista=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_formularios_sin_sesion_redirigen_al_login(self):
        self.client.logout()
        for nombre in ("periodo_nuevo", "proyecto_nuevo"):
            with self.subTest(vista=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 302)
                self.assertTrue(respuesta.url.startswith(reverse("login")))

    def test_post_periodo_valido_guarda_y_redirige(self):
        respuesta = self.client.post(
            reverse("periodo_nuevo"),
            {"nombre": "Ene-Jun 2027", "fecha_inicio": "2027-01-10", "fecha_fin": "2027-06-15"},
            follow=True,
        )
        self.assertTrue(Periodo.objects.filter(nombre="Ene-Jun 2027").exists())
        self.assertContains(respuesta, "Periodo «Ene-Jun 2027» registrado.")

    def test_post_periodo_invalido_no_guarda_y_muestra_error(self):
        respuesta = self.client.post(
            reverse("periodo_nuevo"),
            {"nombre": "Malo", "fecha_inicio": "2027-06-15", "fecha_fin": "2027-01-10"},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Periodo.objects.filter(nombre="Malo").exists())
        self.assertContains(
            respuesta, "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    def test_post_proyecto_valido_guarda_como_activo(self):
        self.client.post(
            reverse("proyecto_nuevo"),
            {
                "nombre": "Dashboard SQA",
                "descripcion": "Monitoreo",
                "lider": self.lider.pk,
                "integrantes": 4,
                "periodo": self.periodo.pk,
            },
        )
        proyecto = Proyecto.objects.get(nombre="Dashboard SQA")
        self.assertEqual(proyecto.estado, "Activo")

    def test_post_proyecto_sin_nombre_no_guarda(self):
        respuesta = self.client.post(
            reverse("proyecto_nuevo"),
            {"nombre": "", "lider": self.lider.pk, "integrantes": 4, "periodo": self.periodo.pk},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Proyecto.objects.count(), 0)
        self.assertContains(respuesta, "Este campo es obligatorio.")
