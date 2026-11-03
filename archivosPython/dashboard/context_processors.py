from django.db.models import Prefetch

from .models import Periodo, Proyecto

# Vistas cuyo `pk` es un proyecto: ese proyecto se resalta en la barra lateral.
VISTAS_DE_PROYECTO = {"editar_proyecto", "metricas_proyecto", "tecnicas_proyecto"}


def navegacion(request):
    """Menú lateral de los mockups: periodos (el más reciente primero) con sus proyectos activos."""
    if not request.user.is_authenticated:
        return {}

    coincidencia = request.resolver_match
    proyecto_actual = None
    if coincidencia and coincidencia.url_name in VISTAS_DE_PROYECTO:
        proyecto_actual = coincidencia.kwargs.get("pk")

    activos = Proyecto.objects.filter(estado=Proyecto.Estado.ACTIVO).order_by("nombre")
    periodos = list(
        Periodo.objects.order_by("-fecha_inicio").prefetch_related(
            Prefetch("proyectos", queryset=activos, to_attr="activos")
        )
    )
    return {
        "nav_periodos": periodos,
        "nav_periodo_actual": periodos[0] if periodos else None,
        "nav_proyecto_actual": proyecto_actual,
    }
