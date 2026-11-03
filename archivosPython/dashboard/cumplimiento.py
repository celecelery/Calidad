"""RF-14: porcentaje de cumplimiento de técnicas SQA de un proyecto.

Cumplimiento = aplicaciones registradas / aplicaciones esperadas en el periodo (RN-13).

Aplicaciones esperadas de cada técnica asignada, según su frecuencia (RF-12):

- «Por corte»: una por cada corte del proyecto hasta el corte que se evalúa.
- «Por PR»: los PRs fusionados acumulados al corte que se evalúa (``Corte.prs_fusionados``).
- «Única»: 1.

Las aplicaciones registradas que cuentan son las que tienen fecha igual o anterior al corte.
Sin corte (pestaña Técnicas SQA) se evalúa hasta el último corte del proyecto.

Si una técnica tiene más aplicaciones de las esperadas, cuenta como 100 %: el excedente no
compensa a las técnicas atrasadas. Una técnica sin aplicaciones esperadas todavía (por
ejemplo «Por PR» sin PRs fusionados) no tiene porcentaje y no entra en el total.
"""

from dataclasses import dataclass, field

from .models import AsignacionTecnica

# Mismos cortes que el semáforo (sección 8 de la SRS) para colorear el porcentaje.
UMBRAL_VERDE = 80
UMBRAL_AMARILLO = 60


def clase_de_porcentaje(porcentaje):
    """Clase CSS de la celda: verde ≥ 80 %, amarillo 60–79 %, rojo < 60 %."""
    if porcentaje is None:
        return ""
    if porcentaje >= UMBRAL_VERDE:
        return "good"
    if porcentaje >= UMBRAL_AMARILLO:
        return "neutral"
    return "bad"


def _porcentaje(cumplidas, esperadas):
    return None if not esperadas else cumplidas * 100 / esperadas


@dataclass
class CumplimientoTecnica:
    """Una fila de la tabla de técnicas: esperadas, registradas y porcentaje."""

    asignacion: AsignacionTecnica
    esperadas: int
    aplicaciones: list = field(default_factory=list)

    @property
    def registradas(self):
        return len(self.aplicaciones)

    @property
    def contadas(self):
        """Registradas que cuentan para el porcentaje (como máximo, las esperadas)."""
        return min(self.registradas, self.esperadas)

    @property
    def porcentaje(self):
        return _porcentaje(self.contadas, self.esperadas)

    @property
    def clase(self):
        return clase_de_porcentaje(self.porcentaje)


@dataclass
class CumplimientoProyecto:
    """Cumplimiento de todas las técnicas asignadas a un proyecto en un corte."""

    tecnicas: list

    @property
    def esperadas(self):
        return sum(t.esperadas for t in self.tecnicas)

    @property
    def registradas(self):
        return sum(t.registradas for t in self.tecnicas)

    @property
    def contadas(self):
        return sum(t.contadas for t in self.tecnicas)

    @property
    def porcentaje(self):
        """None si el proyecto no tiene aplicaciones esperadas (sin técnicas o sin cortes)."""
        return _porcentaje(self.contadas, self.esperadas)

    @property
    def clase(self):
        return clase_de_porcentaje(self.porcentaje)


def esperadas(asignacion, cortes_hasta):
    """Aplicaciones esperadas de una asignación con los cortes del proyecto hasta el evaluado."""
    frecuencia = asignacion.frecuencia
    if frecuencia == AsignacionTecnica.Frecuencia.UNICA:
        return 1
    if frecuencia == AsignacionTecnica.Frecuencia.POR_CORTE:
        return len(cortes_hasta)
    if frecuencia == AsignacionTecnica.Frecuencia.POR_PR:
        return cortes_hasta[-1].prs_fusionados if cortes_hasta else 0
    return 0


def cumplimiento_de_tecnicas(proyecto, corte=None):
    """RF-14: cumplimiento de técnicas del proyecto en un corte (o hasta su último corte)."""
    cortes = list(proyecto.cortes.all())
    if corte is not None:
        cortes = [c for c in cortes if c.fecha <= corte.fecha]
    limite = corte.fecha if corte is not None else None

    asignaciones = (
        proyecto.asignaciones_tecnicas.select_related("tecnica", "usuario")
        .prefetch_related("aplicaciones__registrada_por")
        .order_by("tecnica__nombre")
    )
    filas = []
    for asignacion in asignaciones:
        aplicaciones = [
            a for a in asignacion.aplicaciones.all() if limite is None or a.fecha <= limite
        ]
        filas.append(
            CumplimientoTecnica(
                asignacion=asignacion,
                esperadas=esperadas(asignacion, cortes),
                aplicaciones=aplicaciones,
            )
        )
    return CumplimientoProyecto(tecnicas=filas)
