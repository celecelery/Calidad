"""RF-15: reporte de salud de un proyecto en un corte y su semáforo (sección 8 de la SRS).

Se usa la regla más estricta que aplique, empezando por Rojo (RN-14 y RN-15):

- Rojo: hay al menos un defecto crítico abierto (M-03 > 0), o se cumple menos del 50 % de
  las metas, o el cumplimiento de técnicas SQA es menor al 60 %.
- Verde: se cumple al menos el 83 % de las metas, sin defectos críticos, y el cumplimiento
  de técnicas es de 80 % o más.
- Amarillo: los demás casos (metas entre 50 % y 82 % o técnicas entre 60 % y 79 %).

Todo se calcula con porcentajes para que funcione aunque cambie el número de métricas.
Una métrica asignada sin medición en el corte cuenta como meta no cumplida.

Cuando un dato no existe (el proyecto no tiene métricas, no tiene la métrica M-03 o no tiene
aplicaciones de técnicas esperadas), ese dato no vuelve Rojo al proyecto, pero tampoco se
puede confirmar el Verde: el semáforo queda como máximo en Amarillo y el motivo lo dice.

``semaforo_actual(proyecto)`` da el reporte del último corte; lo usa el dashboard (RF-10).
"""

from dataclasses import dataclass, field

from .cumplimiento import CumplimientoProyecto, cumplimiento_de_tecnicas
from .models import MetricaProyecto

ROJO = "Rojo"
AMARILLO = "Amarillo"
VERDE = "Verde"

# Clave de la métrica «Defectos críticos abiertos» en el catálogo (sección 7 de la SRS).
CLAVE_DEFECTOS_CRITICOS = "M-03"

METAS_VERDE = 83  # % de metas cumplidas: 5 o 6 de 6
METAS_ROJO = 50  # menos de esto es Rojo: 0 a 2 de 6
TECNICAS_VERDE = 80
TECNICAS_ROJO = 60

# Para las plantillas: punto del menú, pastilla y luz encendida del semáforo.
CLASE_SEMAFORO = {ROJO: "r", AMARILLO: "y", VERDE: "g"}


def calcular_semaforo(porcentaje_metas, defectos_criticos, porcentaje_tecnicas):
    """Devuelve Rojo, Amarillo o Verde. Cualquier argumento puede ser None (dato inexistente)."""
    if defectos_criticos is not None and defectos_criticos > 0:
        return ROJO
    if porcentaje_metas is not None and porcentaje_metas < METAS_ROJO:
        return ROJO
    if porcentaje_tecnicas is not None and porcentaje_tecnicas < TECNICAS_ROJO:
        return ROJO
    if (
        porcentaje_metas is not None
        and porcentaje_metas >= METAS_VERDE
        and defectos_criticos is not None
        and porcentaje_tecnicas is not None
        and porcentaje_tecnicas >= TECNICAS_VERDE
    ):
        return VERDE
    return AMARILLO


def _pct(valor):
    return f"{valor:.0f} %"


@dataclass
class FilaMetrica:
    """Una fila de «Métricas contra meta»: la métrica, su medición en el corte y si cumple."""

    metrica: object
    medicion: MetricaProyecto | None

    @property
    def cumple(self):
        return self.metrica.cumple(self.medicion.valor) if self.medicion else False


@dataclass
class ReporteSalud:
    """Reporte de salud calculado (no se guarda; el historial es RF-18)."""

    proyecto: object
    corte: object
    numero_corte: int
    filas: list = field(default_factory=list)
    tecnicas: CumplimientoProyecto | None = None

    # --- metas ---
    @property
    def metas_total(self):
        return len(self.filas)

    @property
    def metas_cumplidas(self):
        return sum(1 for fila in self.filas if fila.cumple)

    @property
    def sin_medicion(self):
        return sum(1 for fila in self.filas if fila.medicion is None)

    @property
    def porcentaje_metas(self):
        if not self.metas_total:
            return None
        return self.metas_cumplidas * 100 / self.metas_total

    # --- defectos críticos (M-03) ---
    @property
    def fila_defectos(self):
        for fila in self.filas:
            if fila.metrica.clave == CLAVE_DEFECTOS_CRITICOS:
                return fila
        return None

    @property
    def defectos_criticos(self):
        """Valor de M-03 en el corte; None si no está asignada o no se capturó."""
        fila = self.fila_defectos
        if fila is None or fila.medicion is None:
            return None
        return fila.medicion.valor

    # --- técnicas ---
    @property
    def porcentaje_tecnicas(self):
        return self.tecnicas.porcentaje if self.tecnicas else None

    # --- semáforo ---
    @property
    def semaforo(self):
        return calcular_semaforo(
            self.porcentaje_metas, self.defectos_criticos, self.porcentaje_tecnicas
        )

    @property
    def clase(self):
        return CLASE_SEMAFORO[self.semaforo]

    @property
    def motivo(self):
        """Explicación en una frase de por qué el semáforo quedó de ese color."""
        metas = self.porcentaje_metas
        criticos = self.defectos_criticos
        tecnicas = self.porcentaje_tecnicas
        texto_metas = (
            f"se cumplen {self.metas_cumplidas} de {self.metas_total} metas ({_pct(metas)})"
            if metas is not None
            else "el proyecto no tiene métricas asignadas"
        )

        if self.semaforo == ROJO:
            motivos = []
            if criticos is not None and criticos > 0:
                n = f"{criticos.normalize():f}"
                plural = "s" if criticos != 1 else ""
                motivos.append(f"hay {n} defecto{plural} crítico{plural} abierto{plural}")
            if metas is not None and metas < METAS_ROJO:
                motivos.append(f"{texto_metas}, menos del {METAS_ROJO} %")
            if tecnicas is not None and tecnicas < TECNICAS_ROJO:
                motivos.append(f"las técnicas van en {_pct(tecnicas)}, menos del {TECNICAS_ROJO} %")
            return _frase(motivos)

        if self.semaforo == VERDE:
            return _frase([
                texto_metas,
                "sin defectos críticos",
                f"con técnicas en {_pct(tecnicas)}",
            ])

        # Amarillo: qué le falta para ser Verde.
        faltas = []
        if metas is None:
            faltas.append(texto_metas)
        elif metas < METAS_VERDE:
            faltas.append(
                f"se cumplen {self.metas_cumplidas} de {self.metas_total} metas "
                f"({_pct(metas)}, entre 50 y 82 %)"
            )
        if criticos is None:
            faltas.append("no hay medición de defectos críticos (M-03) en este corte")
        if tecnicas is None:
            faltas.append("no hay aplicaciones de técnicas esperadas todavía")
        elif tecnicas < TECNICAS_VERDE:
            faltas.append(f"las técnicas van en {_pct(tecnicas)} (entre 60 y 79 %)")
        inicio = "Sin defectos críticos, pero " if criticos is not None else ""
        return inicio + _frase(faltas, mayuscula=not inicio)


def _frase(partes, mayuscula=True):
    if not partes:
        return ""
    texto = partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]
    if mayuscula:
        texto = texto[0].upper() + texto[1:]
    return texto + "."


def reporte_de_salud(proyecto, corte):
    """RF-15: reporte de salud de un proyecto en uno de sus cortes."""
    cortes = list(proyecto.cortes.all())
    numero = next(n for n, c in enumerate(cortes, 1) if c.pk == corte.pk)
    mediciones = {
        m.metrica_id: m
        for m in MetricaProyecto.objects.filter(proyecto=proyecto, corte=corte).select_related(
            "metrica"
        )
    }
    filas = [FilaMetrica(metrica=m, medicion=mediciones.get(m.pk)) for m in proyecto.metricas.all()]
    return ReporteSalud(
        proyecto=proyecto,
        corte=corte,
        numero_corte=numero,
        filas=filas,
        tecnicas=cumplimiento_de_tecnicas(proyecto, corte),
    )


def semaforo_actual(proyecto):
    """Reporte de salud del último corte del proyecto, o None si todavía no tiene cortes."""
    ultimo = proyecto.cortes.last()
    return reporte_de_salud(proyecto, ultimo) if ultimo else None
