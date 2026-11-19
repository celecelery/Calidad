"""Pruebas de RF-18: historial de reportes de salud de un proyecto."""

from datetime import date

from django.urls import reverse

from .models import Corte, Proyecto
from .salud import AMARILLO, ROJO, VERDE, historial_de_salud
from .test_reporte_salud import ReporteBase


class HistorialDeSaludTests(ReporteBase):
    def test_un_reporte_por_corte_del_mas_reciente_al_mas_antiguo(self):
        # Se crea un corte con fecha intermedia después de los otros dos: el orden es por fecha.
        corte_medio = Corte.objects.create(proyecto=self.proyecto, fecha=date(2026, 10, 13))
        historial = historial_de_salud(self.proyecto)
        self.assertEqual(
            [reporte.corte for reporte in historial], [self.corte2, corte_medio, self.corte1]
        )
        self.assertEqual([reporte.numero_corte for reporte in historial], [3, 2, 1])

    def test_cada_corte_tiene_su_propio_semaforo(self):
        self.tecnica_unica()
        self.capturar(self.corte1, self.valores(6, criticos=1))
        self.capturar(self.corte2, self.valores(6))
        historial = historial_de_salud(self.proyecto)
        self.assertEqual([reporte.semaforo for reporte in historial], [VERDE, ROJO])

    def test_corte_sin_mediciones_aparece_en_el_historial(self):
        self.tecnica_unica()
        self.capturar(self.corte1, self.valores(6))
        historial = historial_de_salud(self.proyecto)
        self.assertEqual(len(historial), 2)
        self.assertEqual(historial[0].sin_medicion, 6)
        self.assertEqual(historial[0].semaforo, ROJO)

    def test_sin_cortes_el_historial_esta_vacio(self):
        Corte.objects.filter(proyecto=self.proyecto).delete()
        self.assertEqual(historial_de_salud(self.proyecto), [])

    def test_no_mezcla_cortes_de_otro_proyecto(self):
        otro = Proyecto.objects.create(
            nombre="Otro",
            descripcion="Otro proyecto",
            integrantes=3,
            lider=self.angel,
            periodo=self.periodo,
        )
        Corte.objects.create(proyecto=otro, fecha=date(2026, 10, 27))
        self.assertEqual(len(historial_de_salud(self.proyecto)), 2)


class HistorialVistaTests(ReporteBase):
    def url(self):
        return reverse("historial_salud", args=[self.proyecto.pk])

    def test_lista_los_cortes_con_semaforo_y_enlaces_a_su_reporte(self):
        self.tecnica_unica()
        self.capturar(self.corte1, self.valores(4))
        self.capturar(self.corte2, self.valores(6))
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "dashboard/historial_salud.html")
        self.assertEqual(
            [r.semaforo for r in respuesta.context["reportes"]], [VERDE, AMARILLO]
        )
        contenido = respuesta.content.decode()
        reporte = reverse("reporte_salud", args=[self.proyecto.pk])
        pdf = reverse("reporte_salud_pdf", args=[self.proyecto.pk])
        for corte in (self.corte1, self.corte2):
            self.assertIn(f'href="{reporte}?corte={corte.pk}"', contenido)
            self.assertIn(f'href="{pdf}?corte={corte.pk}"', contenido)
        # El más reciente va primero.
        self.assertLess(contenido.index("20/10/2026"), contenido.index("06/10/2026"))
        self.assertContains(respuesta, "2 cortes en el historial")

    def test_el_enlace_abre_el_reporte_de_ese_corte(self):
        respuesta = self.client.get(
            reverse("reporte_salud", args=[self.proyecto.pk]), {"corte": self.corte1.pk}
        )
        self.assertEqual(respuesta.context["reporte"].corte, self.corte1)

    def test_pestana_historial_activa(self):
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, 'class="tab on"', count=1)
        self.assertContains(respuesta, 'aria-current="page">Historial</a>')

    def test_sin_cortes_muestra_aviso(self):
        Corte.objects.filter(proyecto=self.proyecto).delete()
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, "todavía no tiene cortes")
        self.assertContains(respuesta, "0 cortes en el historial")

    def test_el_reporte_enlaza_al_historial(self):
        respuesta = self.client.get(reverse("reporte_salud", args=[self.proyecto.pk]))
        self.assertContains(respuesta, f'href="{self.url()}"')
        self.assertNotContains(respuesta, "Guardar en historial")

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("historial_salud", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)
