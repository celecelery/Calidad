"""Pruebas de RF-16: comparar el reporte de salud con el corte anterior."""

from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase
from django.urls import reverse

from .models import Corte, Metrica
from .salud import EMPEORO, MEJORO, SE_MANTUVO, reporte_de_salud, tendencia
from .test_reporte_salud import ReporteBase


class TendenciaTests(SimpleTestCase):
    """La tendencia respeta el sentido de la meta de cada métrica."""

    def setUp(self):
        self.cobertura = Metrica(nombre="Cobertura", sentido=Metrica.Sentido.MAYOR_IGUAL)
        self.defectos = Metrica(nombre="Defectos", sentido=Metrica.Sentido.MENOR_IGUAL)

    def test_igual_o_mayor_subir_es_mejorar(self):
        self.assertEqual(tendencia(self.cobertura, Decimal("72"), Decimal("65")), MEJORO)
        self.assertEqual(tendencia(self.cobertura, Decimal("60"), Decimal("65")), EMPEORO)

    def test_igual_o_menor_bajar_es_mejorar(self):
        self.assertEqual(tendencia(self.defectos, Decimal("0"), Decimal("2")), MEJORO)
        self.assertEqual(tendencia(self.defectos, Decimal("3"), Decimal("2")), EMPEORO)

    def test_mismo_valor_se_mantiene(self):
        self.assertEqual(tendencia(self.cobertura, Decimal("70"), Decimal("70.00")), SE_MANTUVO)
        self.assertEqual(tendencia(self.defectos, Decimal("0"), Decimal("0")), SE_MANTUVO)


class ComparacionDelReporteTests(ReporteBase):
    def fila(self, reporte, clave):
        return next(fila for fila in reporte.filas if fila.metrica.clave == clave)

    def test_compara_con_el_corte_anterior(self):
        self.capturar(self.corte1, {"M-01": 65, "M-03": 2})
        self.capturar(self.corte2, {"M-01": 72, "M-03": 0})
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.corte_anterior, self.corte1)
        self.assertEqual(reporte.numero_corte_anterior, 1)
        m01 = self.fila(reporte, "M-01")
        self.assertEqual(m01.anterior.valor, Decimal("65"))
        self.assertEqual((m01.tendencia, m01.clase_tendencia), (MEJORO, "good"))
        # M-03 «Defectos críticos» se cumple con igual o menor: de 2 a 0 es mejorar.
        self.assertEqual(self.fila(reporte, "M-03").tendencia, MEJORO)

    def test_usa_el_corte_anterior_al_elegido_no_el_ultimo(self):
        corte3 = Corte.objects.create(proyecto=self.proyecto, fecha=date(2026, 11, 3))
        self.capturar(self.corte1, {"M-01": 80})
        self.capturar(self.corte2, {"M-01": 72})
        self.capturar(corte3, {"M-01": 90})
        reporte2 = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte2.corte_anterior, self.corte1)
        self.assertEqual(self.fila(reporte2, "M-01").tendencia, EMPEORO)
        reporte3 = reporte_de_salud(self.proyecto, corte3)
        self.assertEqual(reporte3.corte_anterior, self.corte2)
        self.assertEqual(self.fila(reporte3, "M-01").tendencia, MEJORO)

    def test_primer_corte_no_tiene_con_que_compararse(self):
        self.capturar(self.corte1, self.valores(6))
        reporte = reporte_de_salud(self.proyecto, self.corte1)
        self.assertIsNone(reporte.corte_anterior)
        self.assertIsNone(reporte.numero_corte_anterior)
        self.assertEqual(reporte.resumen_comparacion, "")
        self.assertTrue(all(fila.tendencia is None for fila in reporte.filas))

    def test_sin_medicion_en_alguno_de_los_dos_cortes_no_tiene_tendencia(self):
        self.capturar(self.corte1, {"M-01": 65})
        self.capturar(self.corte2, {"M-02": 96})
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertIsNone(self.fila(reporte, "M-01").tendencia)  # falta en el corte 2
        self.assertIsNone(self.fila(reporte, "M-02").tendencia)  # falta en el corte 1
        self.assertEqual(self.fila(reporte, "M-01").clase_tendencia, "gray")

    def test_resumen_de_la_comparacion(self):
        self.capturar(self.corte1, {"M-01": 65, "M-02": 90, "M-04": 95, "M-05": 100, "M-06": 80})
        self.capturar(self.corte2, {"M-01": 72, "M-02": 96, "M-04": 90, "M-05": 100, "M-06": 80})
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(
            reporte.resumen_comparacion,
            "Contra el corte 1: 2 mejoraron, 1 empeoró, 2 se mantuvieron y "
            "1 no se puede comparar.",
        )

    def test_el_semaforo_no_cambia_por_la_comparacion(self):
        # RF-16 solo informa; el semáforo sigue siendo la regla de RF-15 sobre el corte elegido.
        self.capturar(self.corte1, self.valores(6))
        self.capturar(self.corte2, self.valores(6))
        self.tecnica_unica()
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.semaforo, "Verde")
        self.assertEqual(
            reporte.resumen_comparacion, "Contra el corte 1: 6 se mantuvieron."
        )


class ComparacionEnPantallaTests(ReporteBase):
    def url(self):
        return reverse("reporte_salud", args=[self.proyecto.pk])

    def test_tabla_con_corte_anterior_y_tendencia(self):
        self.capturar(self.corte1, {"M-01": 65})
        self.capturar(self.corte2, {"M-01": 72})
        respuesta = self.client.get(self.url())
        self.assertContains(
            respuesta, '<th class="num" title="06/10/2026">Corte 1</th>', html=False
        )
        self.assertContains(respuesta, '<th class="c">Tendencia</th>', html=False)
        self.assertContains(respuesta, '<span class="pill good">Mejoró</span>', html=False)
        self.assertContains(respuesta, "Sin dato")
        self.assertContains(respuesta, "Contra el corte 1: 1 mejoró y 5 no se pueden comparar.")

    def test_al_elegir_el_primer_corte_no_hay_comparacion(self):
        self.capturar(self.corte1, self.valores(6))
        respuesta = self.client.get(self.url(), {"corte": self.corte1.pk})
        self.assertContains(respuesta, "Es el primer corte del proyecto")
        self.assertNotContains(respuesta, "Tendencia")

    def test_ya_no_existe_la_pagina_aparte(self):
        respuesta = self.client.get(f"/proyectos/{self.proyecto.pk}/reporte/comparacion")
        self.assertEqual(respuesta.status_code, 404)
