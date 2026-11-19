"""Pruebas de RF-17: exportar el reporte de salud a PDF.

El contenido se revisa en los textos que van al PDF (``filas_de_metricas``, ``indicadores``...),
porque dentro del PDF el texto queda comprimido y no se puede buscar.
"""

from datetime import date

from django.contrib.messages import get_messages
from django.urls import reverse

from .models import Corte, Proyecto
from .reporte_pdf import (
    aviso_mediciones_faltantes,
    filas_de_metricas,
    filas_de_tecnicas,
    generar_pdf,
    indicadores,
    nombre_archivo,
    texto_comparacion,
)
from .salud import reporte_de_salud
from .test_reporte_salud import ReporteBase

PR_14 = "https://github.com/celecelery/Calidad/pull/14"


class ContenidoDelPdfTests(ReporteBase):
    """Lo que dice el PDF es lo mismo que la pantalla del reporte (RF-15)."""

    def test_tabla_de_metricas_con_valor_meta_y_si_cumple(self):
        self.capturar(self.corte2, self.valores(5))
        filas = filas_de_metricas(reporte_de_salud(self.proyecto, self.corte2))
        self.assertEqual(len(filas), 6)
        cobertura = next(fila for fila in filas if fila[0] == "M-01")
        self.assertEqual(
            cobertura[1:6], ["Cobertura de código", "Pruebas", "72 %", "≥ 70 %", "Sí"]
        )
        self.assertEqual([fila[5] for fila in filas].count("No"), 1)

    def test_comparacion_con_el_corte_anterior(self):
        # RF-16 en el PDF: valor del corte anterior y tendencia, igual que la pantalla.
        self.capturar(self.corte1, {"M-01": 65, "M-03": 2})
        self.capturar(self.corte2, {"M-01": 72, "M-03": 2, "M-04": 92})
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        filas = {fila[0]: fila for fila in filas_de_metricas(reporte)}
        self.assertEqual(filas["M-01"][3:], ["72 %", "≥ 70 %", "Sí", "65 %", "Mejoró"])
        self.assertEqual(filas["M-03"][6:], ["2", "Se mantuvo"])
        self.assertEqual(filas["M-04"][6:], ["Sin medición", "Sin dato"])
        self.assertEqual(filas["M-06"][6:], ["Sin medición", "Sin dato"])
        self.assertEqual(
            texto_comparacion(reporte),
            "Contra el corte 1: 1 mejoró, 1 se mantuvo y 4 no se pueden comparar.",
        )

    def test_primer_corte_sin_comparacion(self):
        self.capturar(self.corte1, self.valores(6))
        reporte = reporte_de_salud(self.proyecto, self.corte1)
        self.assertTrue(all(fila[6:] == ["—", "—"] for fila in filas_de_metricas(reporte)))
        self.assertEqual(
            texto_comparacion(reporte),
            "Es el primer corte del proyecto; todavía no hay corte anterior para comparar.",
        )

    def test_metrica_sin_medicion(self):
        valores = self.valores(6)
        del valores["M-06"]
        self.capturar(self.corte2, valores)
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        fila = next(fila for fila in filas_de_metricas(reporte) if fila[0] == "M-06")
        self.assertEqual((fila[3], fila[5]), ("Sin medición", "No"))
        self.assertEqual(
            aviso_mediciones_faltantes(reporte),
            "Falta 1 medición en este corte; cuenta como meta no cumplida.",
        )

    def test_aviso_de_mediciones_faltantes_en_plural_y_sin_faltantes(self):
        self.capturar(self.corte2, {"M-01": 72, "M-03": 0, "M-04": 92, "M-05": 100})
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(
            aviso_mediciones_faltantes(reporte),
            "Faltan 2 mediciones en este corte; cuentan como metas no cumplidas.",
        )
        self.capturar(self.corte1, self.valores(6))
        completo = reporte_de_salud(self.proyecto, self.corte1)
        self.assertEqual(aviso_mediciones_faltantes(completo), "")

    def test_indicadores(self):
        valores = self.valores(6)
        del valores["M-06"]
        self.capturar(self.corte2, valores)
        self.tecnica_unica()
        self.assertEqual(
            indicadores(reporte_de_salud(self.proyecto, self.corte2)),
            [
                ("Metas cumplidas", "5 / 6", "83 % · 1 sin medición"),
                ("Defectos críticos", "0", "M-03 · issues críticos abiertos"),
                ("Técnicas SQA", "100 %", "1 de 1 aplicaciones"),
            ],
        )

    def test_indicadores_sin_datos(self):
        self.proyecto.metricas.clear()
        self.assertEqual(
            indicadores(reporte_de_salud(self.proyecto, self.corte2)),
            [
                ("Metas cumplidas", "0 / 0", ""),
                ("Defectos críticos", "—", "M-03 sin medición en este corte"),
                ("Técnicas SQA", "—", "0 de 0 aplicaciones"),
            ],
        )

    def test_tecnicas_con_su_evidencia(self):
        self.tecnica_unica()
        self.tecnica_unica(aplicada=False, nombre="Pruebas unitarias")
        filas = filas_de_tecnicas(reporte_de_salud(self.proyecto, self.corte2))
        self.assertIn(
            ["Inspección de requisitos", "Angel Mazón", "Única", "1", "1", "100 %",
             [("01/10/2026", PR_14)]],
            filas,
        )
        self.assertIn(
            ["Pruebas unitarias", "Angel Mazón", "Única", "1", "0", "0 %", []], filas
        )


class GenerarPdfTests(ReporteBase):
    def test_genera_un_pdf(self):
        self.capturar(self.corte2, self.valores(4))
        self.tecnica_unica()
        pdf = generar_pdf(reporte_de_salud(self.proyecto, self.corte2))
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertIn(b"Reporte de salud", pdf)  # título del documento (metadatos)
        self.assertIn(PR_14.encode(), pdf)  # el enlace de la evidencia se puede abrir

    def test_proyecto_sin_metricas_ni_tecnicas(self):
        self.proyecto.metricas.clear()
        pdf = generar_pdf(reporte_de_salud(self.proyecto, self.corte2))
        self.assertTrue(pdf.startswith(b"%PDF-"))

    def test_pdf_con_comparacion(self):
        # Mejoró, empeoró, se mantuvo y sin dato: las cuatro pastillas de la tendencia.
        self.capturar(self.corte1, {"M-01": 65, "M-02": 97, "M-03": 0})
        self.capturar(self.corte2, {"M-01": 72, "M-02": 90, "M-03": 0, "M-04": 92})
        pdf = generar_pdf(reporte_de_salud(self.proyecto, self.corte2))
        self.assertTrue(pdf.startswith(b"%PDF-"))

    def test_proyecto_sin_metricas_con_corte_anterior(self):
        self.proyecto.metricas.clear()
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(texto_comparacion(reporte), "")
        self.assertTrue(generar_pdf(reporte).startswith(b"%PDF-"))

    def test_nombre_con_caracteres_especiales(self):
        # Los textos que escribe el usuario no deben romper el formato de los párrafos.
        self.proyecto.nombre = 'Gestión & <Calidad> "SQA"'
        self.proyecto.save()
        self.capturar(self.corte2, self.valores(6))
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertTrue(generar_pdf(reporte).startswith(b"%PDF-"))
        self.assertEqual(
            nombre_archivo(reporte), "reporte-salud-gestion-calidad-sqa-corte-2-2026-10-20.pdf"
        )

    def test_nombre_de_archivo(self):
        reporte = reporte_de_salud(self.proyecto, self.corte1)
        self.assertEqual(
            nombre_archivo(reporte), "reporte-salud-dashboard-sqa-corte-1-2026-10-06.pdf"
        )


class ExportarPdfVistaTests(ReporteBase):
    def url(self):
        return reverse("reporte_salud_pdf", args=[self.proyecto.pk])

    def assertEsPdf(self, respuesta, archivo):
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertEqual(respuesta["Content-Disposition"], f'attachment; filename="{archivo}"')
        self.assertTrue(respuesta.content.startswith(b"%PDF-"))

    def test_por_omision_exporta_el_ultimo_corte(self):
        self.capturar(self.corte2, self.valores(6))
        respuesta = self.client.get(self.url())
        self.assertEsPdf(respuesta, "reporte-salud-dashboard-sqa-corte-2-2026-10-20.pdf")

    def test_exporta_el_corte_elegido(self):
        respuesta = self.client.get(self.url(), {"corte": self.corte1.pk})
        self.assertEsPdf(respuesta, "reporte-salud-dashboard-sqa-corte-1-2026-10-06.pdf")

    def test_corte_de_otro_proyecto_usa_el_ultimo(self):
        otro = Proyecto.objects.create(
            nombre="Otro", descripcion="x", integrantes=1, lider=self.angel, periodo=self.periodo
        )
        ajeno = Corte.objects.create(proyecto=otro, fecha=date(2026, 10, 6))
        respuesta = self.client.get(self.url(), {"corte": ajeno.pk})
        self.assertEsPdf(respuesta, "reporte-salud-dashboard-sqa-corte-2-2026-10-20.pdf")

    def test_sin_cortes_regresa_al_reporte_con_aviso(self):
        self.proyecto.cortes.all().delete()
        respuesta = self.client.get(self.url())
        self.assertRedirects(respuesta, reverse("reporte_salud", args=[self.proyecto.pk]))
        self.assertEqual(
            [str(m) for m in get_messages(respuesta.wsgi_request)],
            ["El proyecto todavía no tiene cortes; no hay reporte que exportar."],
        )

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("reporte_salud_pdf", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta["Location"].startswith(reverse("login")))


class BotonExportarTests(ReporteBase):
    def url(self):
        return reverse("reporte_salud", args=[self.proyecto.pk])

    def test_el_boton_descarga_el_corte_que_se_esta_viendo(self):
        respuesta = self.client.get(self.url(), {"corte": self.corte1.pk})
        enlace = reverse("reporte_salud_pdf", args=[self.proyecto.pk]) + f"?corte={self.corte1.pk}"
        self.assertContains(respuesta, f'<a class="btn" href="{enlace}"', html=False)
        self.assertNotContains(respuesta, "Próximamente (RF-17)")

    def test_sin_cortes_el_boton_esta_deshabilitado(self):
        self.proyecto.cortes.all().delete()
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, 'title="El proyecto no tiene cortes"', html=False)
        self.assertNotContains(respuesta, reverse("reporte_salud_pdf", args=[self.proyecto.pk]))
