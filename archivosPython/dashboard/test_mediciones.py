"""Pruebas de RF-08 (captura de mediciones por corte), validadas en el servidor (RNF-04)."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import CorteForm, MedicionForm
from .models import Corte, Metrica, MetricaProyecto, Periodo, Proyecto, Usuario


class MedicionesBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="celeste", password="clave-segura-123", first_name="Celeste",
            last_name="Hernández",
        )
        lider = Usuario.objects.create(nombre="Angel", perfil="Miembro")
        cls.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )
        cls.proyecto = Proyecto.objects.create(
            nombre="Dashboard SQA", descripcion="Monitoreo", integrantes=4, lider=lider,
            periodo=cls.periodo,
        )
        cls.otro = Proyecto.objects.create(
            nombre="App de inventario", descripcion="Inventario", integrantes=3, lider=lider,
            periodo=cls.periodo,
        )
        cls.corte1 = Corte.objects.create(proyecto=cls.proyecto, fecha=date(2026, 10, 6))
        cls.corte2 = Corte.objects.create(proyecto=cls.proyecto, fecha=date(2026, 10, 20))
        cls.cobertura = Metrica.objects.get(clave="M-01")
        cls.criticos = Metrica.objects.get(clave="M-03")

    def setUp(self):
        self.client.force_login(self.usuario)

    def datos(self, **cambios):
        datos = {"corte": self.corte2.pk, "metrica": self.cobertura.pk, "valor": "72"}
        datos.update(cambios)
        return datos

    def capturar(self, **cambios):
        return self.client.post(
            reverse("capturar_medicion", args=[self.proyecto.pk]), self.datos(**cambios)
        )


FUERA_DE_RANGO_PORCENTAJE = "Fuera de rango: un porcentaje va de 0 a 100."


class MedicionFormTests(MedicionesBaseTest):
    """RF-08: no acepta valores fuera del rango de la unidad."""

    def form(self, **cambios):
        return MedicionForm(data=self.datos(**cambios), proyecto=self.proyecto)

    def assertErrorEnValor(self, form, mensaje):
        self.assertFalse(form.is_valid())
        self.assertIn(mensaje, form.errors["valor"])

    def test_porcentaje_valido_se_acepta(self):
        self.assertTrue(self.form(valor="72.5").is_valid())

    def test_limites_del_porcentaje_se_aceptan(self):
        self.assertTrue(self.form(valor="0").is_valid())
        self.assertTrue(self.form(valor="100").is_valid())

    def test_porcentaje_mayor_a_100_se_rechaza(self):
        self.assertErrorEnValor(self.form(valor="105"), FUERA_DE_RANGO_PORCENTAJE)

    def test_porcentaje_negativo_se_rechaza(self):
        self.assertErrorEnValor(self.form(valor="-1"), FUERA_DE_RANGO_PORCENTAJE)

    def test_conteo_negativo_se_rechaza(self):
        self.assertErrorEnValor(
            self.form(metrica=self.criticos.pk, valor="-2"),
            "Fuera de rango: un conteo no puede ser negativo.",
        )

    def test_conteo_con_decimales_se_rechaza(self):
        self.assertErrorEnValor(
            self.form(metrica=self.criticos.pk, valor="1.5"), "Un conteo es un número entero."
        )

    def test_conteo_mayor_a_100_se_acepta(self):
        self.assertTrue(self.form(metrica=self.criticos.pk, valor="150").is_valid())

    def test_valor_no_numerico_se_rechaza(self):
        self.assertErrorEnValor(self.form(valor="setenta"), "Escribe un número.")

    def test_mas_de_dos_decimales_se_rechaza(self):
        self.assertErrorEnValor(self.form(valor="72.555"), "Usa como máximo 2 decimales.")

    def test_campos_obligatorios(self):
        form = MedicionForm(data={}, proyecto=self.proyecto)
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"corte", "metrica", "valor"})

    def test_metrica_no_asignada_se_rechaza(self):
        self.proyecto.metricas.remove(self.cobertura)
        form = self.form()
        self.assertFalse(form.is_valid())
        self.assertIn("Selecciona una métrica asignada a este proyecto.", form.errors["metrica"])

    def test_corte_de_otro_proyecto_se_rechaza(self):
        ajeno = Corte.objects.create(proyecto=self.otro, fecha=date(2026, 10, 6))
        form = self.form(corte=ajeno.pk)
        self.assertFalse(form.is_valid())
        self.assertIn("Selecciona un corte de este proyecto.", form.errors["corte"])

    def test_cortes_se_numeran_por_fecha(self):
        Corte.objects.create(proyecto=self.proyecto, fecha=date(2026, 9, 1))
        etiquetas = [etiqueta for _, etiqueta in self.form().fields["corte"].choices][1:]
        self.assertEqual(
            etiquetas, ["Corte 1 — 01/09/2026", "Corte 2 — 06/10/2026", "Corte 3 — 20/10/2026"]
        )


class CorteFormTests(MedicionesBaseTest):
    def form(self, fecha):
        return CorteForm(data={"fecha": fecha}, proyecto=self.proyecto)

    def test_fecha_dentro_del_periodo_se_acepta(self):
        self.assertTrue(self.form("2026-11-03").is_valid())

    def test_limites_del_periodo_se_aceptan(self):
        self.assertTrue(self.form("2026-08-10").is_valid())
        self.assertTrue(self.form("2026-12-15").is_valid())

    def test_fecha_fuera_del_periodo_se_rechaza(self):
        form = self.form("2026-12-16")
        self.assertFalse(form.is_valid())
        self.assertIn("El corte debe caer dentro del periodo Ago-Dic 2026", form.errors["fecha"][0])

    def test_fecha_repetida_se_rechaza(self):
        form = self.form("2026-10-20")
        self.assertFalse(form.is_valid())
        self.assertIn("El proyecto ya tiene un corte en esa fecha.", form.errors["fecha"])

    def test_misma_fecha_en_otro_proyecto_se_acepta(self):
        form = CorteForm(data={"fecha": "2026-10-20"}, proyecto=self.otro)
        self.assertTrue(form.is_valid())


class CapturarMedicionVistaTests(MedicionesBaseTest):
    def test_post_valido_guarda_la_medicion_y_quien_la_capturo(self):
        respuesta = self.capturar()
        self.assertRedirects(respuesta, reverse("metricas_proyecto", args=[self.proyecto.pk]))
        medicion = MetricaProyecto.objects.get(proyecto=self.proyecto, corte=self.corte2)
        self.assertEqual(medicion.valor, Decimal("72"))
        self.assertEqual(medicion.capturado_por, self.usuario)

    def test_capturar_otra_vez_corrige_el_valor(self):
        self.capturar(valor="65")
        respuesta = self.capturar(valor="72")
        self.assertEqual(MetricaProyecto.objects.filter(corte=self.corte2).count(), 1)
        self.assertEqual(MetricaProyecto.objects.get(corte=self.corte2).valor, Decimal("72"))
        self.assertRedirects(respuesta, reverse("metricas_proyecto", args=[self.proyecto.pk]))

    def test_mensaje_dice_metrica_y_corte(self):
        respuesta = self.client.post(
            reverse("capturar_medicion", args=[self.proyecto.pk]), self.datos(), follow=True
        )
        self.assertContains(
            respuesta, "Medición de «M-01 Cobertura de código» en Corte 2 — 20/10/2026 guardada."
        )

    def test_valor_fuera_de_rango_no_se_guarda_y_muestra_el_error(self):
        respuesta = self.capturar(valor="105")
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(MetricaProyecto.objects.exists())
        self.assertContains(respuesta, "Fuera de rango: un porcentaje va de 0 a 100.")
        self.assertContains(respuesta, "1 error en la captura")
        self.assertContains(respuesta, 'value="105"')

    def test_solo_acepta_post(self):
        respuesta = self.client.get(reverse("capturar_medicion", args=[self.proyecto.pk]))
        self.assertEqual(respuesta.status_code, 405)

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.post(reverse("capturar_medicion", args=[9999]), self.datos())
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_sesion_no_guarda(self):
        self.client.logout()
        respuesta = self.capturar()
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(MetricaProyecto.objects.exists())


class AgregarCorteVistaTests(MedicionesBaseTest):
    def test_post_valido_agrega_el_corte(self):
        respuesta = self.client.post(
            reverse("agregar_corte", args=[self.proyecto.pk]), {"fecha": "2026-11-03"},
            follow=True,
        )
        self.assertRedirects(respuesta, reverse("metricas_proyecto", args=[self.proyecto.pk]))
        self.assertTrue(self.proyecto.cortes.filter(fecha=date(2026, 11, 3)).exists())
        self.assertContains(respuesta, "Corte 3 — 03/11/2026 agregado.")

    def test_fecha_fuera_del_periodo_muestra_el_error_con_el_formulario_abierto(self):
        respuesta = self.client.post(
            reverse("agregar_corte", args=[self.proyecto.pk]), {"fecha": "2027-01-10"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["abrir_corte"])
        self.assertContains(respuesta, "El corte debe caer dentro del periodo")
        self.assertEqual(self.proyecto.cortes.count(), 2)

    def test_solo_acepta_post(self):
        respuesta = self.client.get(reverse("agregar_corte", args=[self.proyecto.pk]))
        self.assertEqual(respuesta.status_code, 405)


class TablaMedicionesTests(MedicionesBaseTest):
    """Tabla «Mediciones del periodo» del mockup: una columna por corte y metas cumplidas."""

    def medir(self, metrica, corte, valor):
        MetricaProyecto.objects.create(
            proyecto=self.proyecto, metrica=metrica, corte=corte, valor=Decimal(valor),
            capturado_por=self.usuario,
        )

    def pagina(self):
        return self.client.get(reverse("metricas_proyecto", args=[self.proyecto.pk]))

    def fila(self, respuesta, clave):
        return next(f for f in respuesta.context["filas"] if f["metrica"].clave == clave)

    def test_una_columna_por_corte(self):
        respuesta = self.pagina()
        self.assertContains(respuesta, "Corte 1 · 06/10")
        self.assertContains(respuesta, "Corte 2 · 20/10")

    def test_celdas_marcan_si_cumplen_la_meta(self):
        self.medir(self.cobertura, self.corte1, "58")
        self.medir(self.cobertura, self.corte2, "72")
        self.medir(self.criticos, self.corte2, "0")
        respuesta = self.pagina()
        celdas = self.fila(respuesta, "M-01")["celdas"]
        self.assertEqual([c["cumple"] for c in celdas], [False, True])
        self.assertContains(respuesta, "58 %")
        self.assertContains(respuesta, "72 %")

    def test_metas_cumplidas_por_corte_y_pendientes(self):
        self.medir(self.cobertura, self.corte2, "72")
        self.medir(self.criticos, self.corte2, "1")
        respuesta = self.pagina()
        self.assertEqual(
            respuesta.context["totales"],
            [{"cumplidas": 0, "capturadas": 0}, {"cumplidas": 1, "capturadas": 2}],
        )
        self.assertContains(respuesta, "4 pendientes")
        self.assertContains(respuesta, "2 de 6 mediciones capturadas en el corte 2")

    def test_capturo_muestra_el_nombre_del_usuario(self):
        self.medir(self.cobertura, self.corte2, "72")
        self.assertContains(self.pagina(), "Celeste Hernández")

    def test_propone_el_ultimo_corte_y_la_primera_metrica_pendiente(self):
        self.medir(self.cobertura, self.corte2, "72")
        formulario = self.pagina().context["form_medicion"]
        self.assertEqual(formulario["corte"].value(), self.corte2.pk)
        self.assertEqual(formulario["metrica"].value(), Metrica.objects.get(clave="M-02").pk)

    def test_mediciones_de_otro_proyecto_no_aparecen(self):
        corte = Corte.objects.create(proyecto=self.otro, fecha=date(2026, 10, 6))
        MetricaProyecto.objects.create(
            proyecto=self.otro, metrica=self.cobertura, corte=corte, valor=Decimal("99")
        )
        self.assertNotContains(self.pagina(), "99 %")

    def test_sin_cortes_abre_el_formulario_de_corte(self):
        respuesta = self.client.get(reverse("metricas_proyecto", args=[self.otro.pk]))
        self.assertTrue(respuesta.context["abrir_corte"])
        self.assertIsNone(respuesta.context["ultimo"])
        self.assertContains(respuesta, "Sin cortes todavía")

    def test_detalle_para_la_linea_fx(self):
        detalle = self.pagina().context["detalle_metricas"]
        self.assertEqual(
            detalle[str(self.cobertura.pk)],
            {
                "fx": "M-01 = líneas cubiertas / líneas totales × 100 · Meta ≥ 70 % "
                "· Fuente: Reporte de pytest-cov",
                "unidad": "%",
            },
        )
        self.assertEqual(detalle[str(self.criticos.pk)]["unidad"], "")


class MigracionCortesTests(TestCase):
    """La migración 0005 cambia el corte de texto a fecha (observación (b) de la bitácora)."""

    def test_corte_es_una_fecha_unica_por_proyecto(self):
        campo = Corte._meta.get_field("fecha")
        self.assertEqual(campo.get_internal_type(), "DateField")
        restricciones = {r.name for r in Corte._meta.constraints}
        self.assertIn("corte_unico_por_fecha", restricciones)
