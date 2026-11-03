"""Pruebas unitarias de los cálculos del semáforo y del cumplimiento (tarea 10.3).

Cubren los casos de datos incompletos que el reporte debe explicar (CP-15-03, CP-15-10 y
CP-14-06 en `Bitacora SQA/casos_de_prueba.md`), sin base de datos: se arman las métricas,
mediciones y técnicas en memoria.
"""

from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from .cumplimiento import CumplimientoProyecto, CumplimientoTecnica, esperadas
from .models import Metrica, MetricaProyecto
from .salud import AMARILLO, VERDE, FilaMetrica, ReporteSalud, _frase


def fila(clave, valor, meta=70, sentido=">="):
    metrica = Metrica(clave=clave, nombre=clave, unidad="%", meta=Decimal(meta), sentido=sentido)
    medicion = MetricaProyecto(valor=Decimal(valor)) if valor is not None else None
    return FilaMetrica(metrica=metrica, medicion=medicion)


def tecnicas(registradas, esperadas_):
    tecnica = CumplimientoTecnica(
        asignacion=None, esperadas=esperadas_, aplicaciones=[object()] * registradas
    )
    return CumplimientoProyecto(tecnicas=[tecnica])


def reporte(filas, cumplimiento=None):
    return ReporteSalud(
        proyecto=None, corte=None, numero_corte=1, filas=filas, tecnicas=cumplimiento
    )


SEIS_QUE_CUMPLEN = [fila(f"M-0{n}", "80") for n in (1, 2, 4, 5, 6)] + [
    fila("M-03", "0", meta=0, sentido="<=")
]


class MotivoDelSemaforoTests(SimpleTestCase):
    """El reporte explica por qué no llegó a Verde cuando falta un dato (sección 8 de la SRS)."""

    def test_cp_15_10_sin_metricas_asignadas(self):
        sin_metricas = reporte([], tecnicas(1, 1))
        self.assertIsNone(sin_metricas.porcentaje_metas)
        self.assertIsNone(sin_metricas.defectos_criticos)
        self.assertEqual(sin_metricas.semaforo, AMARILLO)
        self.assertEqual(
            sin_metricas.motivo,
            "El proyecto no tiene métricas asignadas y no hay medición de defectos críticos "
            "(M-03) en este corte.",
        )

    def test_cp_15_10_m03_asignada_pero_sin_medicion(self):
        sin_m03 = reporte(SEIS_QUE_CUMPLEN[:5] + [fila("M-03", None, 0, "<=")], tecnicas(1, 1))
        self.assertIsNone(sin_m03.defectos_criticos)
        self.assertEqual(sin_m03.semaforo, AMARILLO)
        self.assertEqual(
            sin_m03.motivo, "No hay medición de defectos críticos (M-03) en este corte."
        )

    def test_cp_15_03_tecnicas_entre_60_y_79_lo_explica(self):
        atrasadas = reporte(SEIS_QUE_CUMPLEN, tecnicas(7, 10))
        self.assertEqual(atrasadas.porcentaje_tecnicas, 70)
        self.assertEqual(atrasadas.semaforo, AMARILLO)
        self.assertEqual(
            atrasadas.motivo,
            "Sin defectos críticos, pero las técnicas van en 70 % (entre 60 y 79 %).",
        )

    def test_verde_lo_explica(self):
        al_dia = reporte(SEIS_QUE_CUMPLEN, tecnicas(2, 2))
        self.assertEqual(al_dia.semaforo, VERDE)
        self.assertEqual(
            al_dia.motivo,
            "Se cumplen 6 de 6 metas (100 %), sin defectos críticos y con técnicas en 100 %.",
        )

    def test_frase_vacia(self):
        self.assertEqual(_frase([]), "")


class EsperadasFrecuenciaTests(SimpleTestCase):
    def test_cp_14_06_frecuencia_desconocida_no_espera_aplicaciones(self):
        self.assertEqual(esperadas(SimpleNamespace(frecuencia="Mensual"), cortes_hasta=[1, 2]), 0)
