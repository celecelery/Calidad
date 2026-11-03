"""Pruebas de RF-15: reporte de salud de un proyecto en un corte y su semáforo."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import (
    AplicacionTecnica,
    AsignacionTecnica,
    Corte,
    Metrica,
    MetricaProyecto,
    Periodo,
    Proyecto,
    TecnicaSQA,
    Usuario,
)
from .salud import AMARILLO, ROJO, VERDE, calcular_semaforo, reporte_de_salud, semaforo_actual

# Valores que cumplen y que no cumplen la meta de cada métrica base (sección 7 de la SRS).
CUMPLE = {"M-01": 72, "M-02": 96, "M-03": 0, "M-04": 92, "M-05": 100, "M-06": 91}
NO_CUMPLE = {"M-01": 65, "M-02": 90, "M-03": 1, "M-04": 85, "M-05": 95, "M-06": 80}


class CalcularSemaforoTests(SimpleTestCase):
    """Regla de la sección 8 de la SRS, la más estricta primero (RN-14 y RN-15)."""

    def test_verde(self):
        self.assertEqual(calcular_semaforo(100, 0, 100), VERDE)

    def test_rojo_por_un_defecto_critico_aunque_lo_demas_este_bien(self):
        self.assertEqual(calcular_semaforo(100, 1, 100), ROJO)

    def test_rojo_por_menos_del_50_por_ciento_de_metas(self):
        self.assertEqual(calcular_semaforo(49.9, 0, 100), ROJO)

    def test_rojo_por_tecnicas_menores_a_60(self):
        self.assertEqual(calcular_semaforo(100, 0, 59.9), ROJO)

    def test_amarillo_por_metas_entre_50_y_82(self):
        self.assertEqual(calcular_semaforo(50, 0, 100), AMARILLO)
        self.assertEqual(calcular_semaforo(82.9, 0, 100), AMARILLO)

    def test_amarillo_por_tecnicas_entre_60_y_79(self):
        self.assertEqual(calcular_semaforo(100, 0, 60), AMARILLO)
        self.assertEqual(calcular_semaforo(100, 0, 79.9), AMARILLO)

    def test_limites_del_verde(self):
        self.assertEqual(calcular_semaforo(83, 0, 80), VERDE)
        self.assertEqual(calcular_semaforo(5 * 100 / 6, 0, 80), VERDE)

    def test_metas_de_6_metricas(self):
        resultados = {n: calcular_semaforo(n * 100 / 6, 0, 100) for n in range(7)}
        self.assertEqual(
            resultados,
            {0: ROJO, 1: ROJO, 2: ROJO, 3: AMARILLO, 4: AMARILLO, 5: VERDE, 6: VERDE},
        )

    def test_funciona_con_otro_numero_de_metricas(self):
        # Con 7 métricas: 6/7 = 86 % es Verde y 3/7 = 43 % es Rojo.
        self.assertEqual(calcular_semaforo(6 * 100 / 7, 0, 100), VERDE)
        self.assertEqual(calcular_semaforo(3 * 100 / 7, 0, 100), ROJO)

    def test_rojo_gana_aunque_tambien_aplique_amarillo(self):
        self.assertEqual(calcular_semaforo(66, 0, 50), ROJO)

    def test_sin_tecnicas_esperadas_no_puede_ser_verde(self):
        self.assertEqual(calcular_semaforo(100, 0, None), AMARILLO)

    def test_sin_medicion_de_defectos_no_puede_ser_verde(self):
        self.assertEqual(calcular_semaforo(100, None, 100), AMARILLO)

    def test_sin_metricas_no_puede_ser_verde(self):
        self.assertEqual(calcular_semaforo(None, 0, 100), AMARILLO)

    def test_dato_inexistente_no_quita_el_rojo(self):
        self.assertEqual(calcular_semaforo(40, None, None), ROJO)


class ReporteBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="angel", password="clave-segura-123"
        )
        cls.angel = Usuario.objects.create(nombre="Angel Mazón", perfil="Administrador")
        cls.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )

    def setUp(self):
        self.client.force_login(self.usuario)
        self.proyecto = Proyecto.objects.create(
            nombre="Dashboard SQA",
            descripcion="Proyecto de prueba",
            integrantes=4,
            lider=self.angel,
            periodo=self.periodo,
        )
        self.corte1 = Corte.objects.create(proyecto=self.proyecto, fecha=date(2026, 10, 6))
        self.corte2 = Corte.objects.create(proyecto=self.proyecto, fecha=date(2026, 10, 20))

    def capturar(self, corte, valores):
        for clave, valor in valores.items():
            MetricaProyecto.objects.create(
                proyecto=self.proyecto,
                metrica=Metrica.objects.get(clave=clave),
                corte=corte,
                valor=Decimal(valor),
            )

    def valores(self, cumplen, **extra):
        """`cumplen` métricas cumplen la meta (M-03 siempre en 0 salvo que se indique)."""
        claves = ["M-03", "M-01", "M-02", "M-04", "M-05", "M-06"]
        valores = {
            clave: CUMPLE[clave] if i < cumplen else NO_CUMPLE[clave]
            for i, clave in enumerate(claves)
        }
        valores["M-03"] = extra.pop("criticos", 0)
        valores.update(extra)
        return valores

    def tecnica_unica(self, aplicada=True, nombre="Inspección de requisitos"):
        asignacion = AsignacionTecnica.objects.create(
            proyecto=self.proyecto,
            tecnica=TecnicaSQA.objects.get(nombre=nombre),
            usuario=self.angel,
            frecuencia="Única",
        )
        if aplicada:
            AplicacionTecnica.objects.create(
                asignacion=asignacion,
                fecha=date(2026, 10, 1),
                evidencia="https://github.com/celecelery/Calidad/pull/14",
                resultado="Favorable",
                registrada_por=self.angel,
            )
        return asignacion


class ReporteDeSaludTests(ReporteBase):
    def test_verde_con_5_de_6_metas_sin_criticos_y_tecnicas_al_100(self):
        self.capturar(self.corte2, self.valores(5))
        self.tecnica_unica()
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (5, 6))
        self.assertEqual(reporte.defectos_criticos, 0)
        self.assertEqual(reporte.porcentaje_tecnicas, 100)
        self.assertEqual(reporte.semaforo, VERDE)
        self.assertEqual(
            reporte.motivo, "Se cumplen 5 de 6 metas (83 %), sin defectos críticos y con "
            "técnicas en 100 %."
        )

    def test_amarillo_con_4_de_6_metas(self):
        self.capturar(self.corte2, self.valores(4))
        self.tecnica_unica()
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.semaforo, AMARILLO)
        self.assertEqual(
            reporte.motivo,
            "Sin defectos críticos, pero se cumplen 4 de 6 metas (67 %, entre 50 y 82 %).",
        )

    def test_rojo_con_un_defecto_critico_respeta_el_sentido_de_m03(self):
        # M-03 se cumple con valor igual o menor a 0: un defecto crítico no cumple y es Rojo.
        self.capturar(self.corte2, self.valores(6, criticos=1))
        self.tecnica_unica()
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.metas_cumplidas, 5)
        self.assertEqual(reporte.semaforo, ROJO)
        self.assertEqual(reporte.motivo, "Hay 1 defecto crítico abierto.")

    def test_rojo_con_2_de_6_metas_y_tecnicas_bajas(self):
        self.capturar(self.corte2, self.valores(2))
        self.tecnica_unica(aplicada=False)
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.semaforo, ROJO)
        self.assertEqual(
            reporte.motivo,
            "Se cumplen 2 de 6 metas (33 %), menos del 50 % y las técnicas van en 0 %, "
            "menos del 60 %.",
        )

    def test_medicion_faltante_cuenta_como_meta_no_cumplida(self):
        valores = self.valores(6)
        del valores["M-06"]
        self.capturar(self.corte2, valores)
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (5, 6))
        self.assertEqual(reporte.sin_medicion, 1)

    def test_corte_sin_mediciones_es_rojo(self):
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.metas_cumplidas, 0)
        self.assertIsNone(reporte.defectos_criticos)
        self.assertEqual(reporte.semaforo, ROJO)

    def test_sin_tecnicas_queda_en_amarillo_y_lo_explica(self):
        self.capturar(self.corte2, self.valores(6))
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        self.assertEqual(reporte.semaforo, AMARILLO)
        self.assertIn("no hay aplicaciones de técnicas esperadas todavía", reporte.motivo)

    def test_usa_las_mediciones_del_corte_elegido(self):
        self.capturar(self.corte1, self.valores(2))
        self.capturar(self.corte2, self.valores(6))
        self.tecnica_unica()
        self.assertEqual(reporte_de_salud(self.proyecto, self.corte1).semaforo, ROJO)
        self.assertEqual(reporte_de_salud(self.proyecto, self.corte2).semaforo, VERDE)
        self.assertEqual(reporte_de_salud(self.proyecto, self.corte1).numero_corte, 1)

    def test_metrica_extra_cambia_el_porcentaje(self):
        extra = Metrica.objects.create(
            clave="M-07", nombre="Densidad de defectos", tipo="Producto", formula="d / KLOC",
            unidad="conteo", meta=Decimal("2"), sentido="<=",
        )
        self.proyecto.metricas.add(extra)
        self.capturar(self.corte2, {**self.valores(5), "M-07": 5})
        self.tecnica_unica()
        reporte = reporte_de_salud(self.proyecto, self.corte2)
        # 5 de 7 = 71 %: con 7 métricas ya no alcanza el 83 % del Verde.
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (5, 7))
        self.assertEqual(reporte.semaforo, AMARILLO)

    def test_semaforo_actual_usa_el_ultimo_corte(self):
        self.capturar(self.corte1, self.valores(6))
        self.capturar(self.corte2, self.valores(1))
        self.assertEqual(semaforo_actual(self.proyecto).corte, self.corte2)
        self.assertEqual(semaforo_actual(self.proyecto).semaforo, ROJO)

    def test_semaforo_actual_sin_cortes_es_none(self):
        self.proyecto.cortes.all().delete()
        self.assertIsNone(semaforo_actual(self.proyecto))


class ReporteVistaTests(ReporteBase):
    def url(self):
        return reverse("reporte_salud", args=[self.proyecto.pk])

    def test_por_omision_muestra_el_ultimo_corte(self):
        self.capturar(self.corte2, self.valores(4))
        self.tecnica_unica()
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.status_code, 200)
        reporte = respuesta.context["reporte"]
        self.assertEqual(reporte.corte, self.corte2)
        self.assertContains(respuesta, "AMARILLO")
        self.assertContains(respuesta, "Semáforo general · Corte 2")
        self.assertContains(respuesta, '<span class="luz y on"></span>', html=False)
        self.assertContains(respuesta, "4 / 6")

    def test_elegir_otro_corte(self):
        self.capturar(self.corte1, self.valores(1))
        respuesta = self.client.get(self.url(), {"corte": self.corte1.pk})
        self.assertEqual(respuesta.context["reporte"].corte, self.corte1)
        self.assertContains(respuesta, "ROJO")

    def test_corte_de_otro_proyecto_usa_el_ultimo(self):
        otro = Proyecto.objects.create(
            nombre="Otro", descripcion="x", integrantes=1, lider=self.angel, periodo=self.periodo
        )
        ajeno = Corte.objects.create(proyecto=otro, fecha=date(2026, 10, 6))
        respuesta = self.client.get(self.url(), {"corte": ajeno.pk})
        self.assertEqual(respuesta.context["reporte"].corte, self.corte2)

    def test_tabla_de_metricas_con_valor_meta_y_si_cumple(self):
        self.capturar(self.corte2, self.valores(5))
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, "Cobertura de código")
        self.assertContains(respuesta, "≥ 70 %")
        self.assertContains(respuesta, '<td class="c good">Sí</td>', count=5, html=False)
        self.assertContains(respuesta, '<td class="c bad">No</td>', count=1, html=False)

    def test_tecnicas_con_enlaces_de_evidencia(self):
        self.tecnica_unica()
        self.tecnica_unica(aplicada=False, nombre="Pruebas unitarias")
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, 'href="https://github.com/celecelery/Calidad/pull/14"')
        self.assertContains(respuesta, "Sin evidencia")
        self.assertContains(respuesta, "1 de 2 aplicaciones")

    def test_sin_cortes_avisa(self):
        self.proyecto.cortes.all().delete()
        respuesta = self.client.get(self.url())
        self.assertIsNone(respuesta.context["reporte"])
        self.assertContains(respuesta, "El proyecto todavía no tiene cortes.")

    def test_pestana_activa(self):
        respuesta = self.client.get(self.url())
        self.assertContains(
            respuesta, f'<a class="tab on" href="{self.url()}" aria-current="page">', html=False
        )

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("reporte_salud", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)
