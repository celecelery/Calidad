from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)
from .forms import (
    AsignacionTecnicaForm,
    AsignarMetricaForm,
    FiltroProyectosForm,
    MetricaForm,
    PeriodoForm,
    ProyectoForm,
    TecnicaSQAForm,
)
from .models import Metrica, Proyecto, TecnicaSQA


def periodo_view(request):
    """RF-01: formulario para registrar un periodo."""
    if request.method == "POST":
        formulario = PeriodoForm(request.POST)
        if formulario.is_valid():
            periodo = formulario.save()
            messages.success(request, f"Periodo «{periodo.nombre}» registrado.")
            return redirect("periodo_nuevo")
    else:
        formulario = PeriodoForm()

    return render(request, "dashboard/formulario_periodo.html", {"formulario": formulario})


def proyecto_view(request):
    """RF-02: formulario para registrar un proyecto."""
    if request.method == "POST":
        formulario = ProyectoForm(request.POST)
        if formulario.is_valid():
            proyecto = formulario.save(commit=False)
            proyecto.estado = "Activo"
            proyecto.save()
            messages.success(request, f"Proyecto «{proyecto.nombre}» registrado.")
            return redirect("proyecto_nuevo")
    else:
        formulario = ProyectoForm()

    # RF-07: el mockup muestra al lado las métricas base que recibirá el proyecto.
    return render(
        request,
        "dashboard/formulario_proyecto.html",
        {"formulario": formulario, "metricas_base": Metrica.objects.filter(es_base=True)},
    )


def lista_proyectos(request):
    """RF-04: lista de proyectos filtrada por periodo y estado (los dos filtros se combinan)."""
    proyectos = Proyecto.objects.select_related("periodo", "lider").order_by("nombre")
    filtro = FiltroProyectosForm(request.GET or None)

    if filtro.is_valid():
        periodo = filtro.cleaned_data.get("periodo")
        estado = filtro.cleaned_data.get("estado")
        if periodo:
            proyectos = proyectos.filter(periodo=periodo)
        if estado:
            proyectos = proyectos.filter(estado=estado)

    return render(
        request,
        "dashboard/lista_proyectos.html",
        {"proyectos": proyectos, "filtro": filtro},
    )


def editar_proyecto(request, pk):
    """RF-03: editar los datos de un proyecto; solo se modifica ese proyecto."""
    proyecto = get_object_or_404(Proyecto.objects.select_related("periodo", "lider"), pk=pk)

    if request.method == "POST":
        formulario = ProyectoForm(request.POST, instance=proyecto)
        if formulario.is_valid():
            proyecto = formulario.save()
            messages.success(request, f"Proyecto «{proyecto.nombre}» actualizado.")
            return redirect("lista_proyectos")
    else:
        formulario = ProyectoForm(instance=proyecto)

    return render(
        request,
        "dashboard/editar_proyecto.html",
        {"formulario": formulario, "proyecto": proyecto},
    )


def metricas_view(request, pk=None):
    """RF-06: catálogo de métricas con el formulario al lado (nueva o la seleccionada)."""
    metrica = get_object_or_404(Metrica, pk=pk) if pk else None

    if request.method == "POST":
        formulario = MetricaForm(request.POST, instance=metrica)
        if formulario.is_valid():
            guardada = formulario.save()
            accion = "actualizada" if metrica else "registrada"
            messages.success(request, f"Métrica «{guardada.nombre}» {accion}.")
            return redirect("editar_metrica", pk=guardada.pk)
    else:
        formulario = MetricaForm(instance=metrica)

    return render(
        request,
        "dashboard/lista_metricas.html",
        {"metricas": Metrica.objects.all(), "formulario": formulario, "metrica": metrica},
    )


def metricas_proyecto(request, pk):
    """RF-07: métricas asignadas a un proyecto y formulario para asignar otra."""
    proyecto = get_object_or_404(Proyecto.objects.select_related("periodo", "lider"), pk=pk)
    datos = request.POST if request.method == "POST" else None
    formulario = AsignarMetricaForm(datos, proyecto=proyecto)

    if formulario.is_valid():
        metrica = formulario.cleaned_data["metrica"]
        proyecto.metricas.add(metrica)
        messages.success(request, f"Métrica «{metrica}» asignada a «{proyecto.nombre}».")
        return redirect("metricas_proyecto", pk=proyecto.pk)

    return render(
        request,
        "dashboard/metricas_proyecto.html",
        {"formulario": formulario, "proyecto": proyecto, "metricas": proyecto.metricas.all()},
    )


@require_POST
def quitar_metrica(request, pk, metrica_pk):
    """RF-07: quitar una métrica de un proyecto; no la borra del catálogo ni de otros proyectos."""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    metrica = get_object_or_404(proyecto.metricas, pk=metrica_pk)
    proyecto.metricas.remove(metrica)
    messages.success(request, f"Métrica «{metrica}» quitada de «{proyecto.nombre}».")
    return redirect("metricas_proyecto", pk=proyecto.pk)


def _catalogo_tecnicas(request, formulario, tecnica=None):
    """RF-11: pantalla del catálogo con el panel lateral para agregar o editar una técnica."""
    busqueda = request.GET.get("q", "").strip()
    tecnicas = TecnicaSQA.objects.annotate(en_uso=Count("asignaciones")).order_by("nombre")
    if busqueda:
        tecnicas = tecnicas.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )
    return render(
        request,
        "dashboard/lista_tecnicas.html",
        {
            "tecnicas": tecnicas,
            "busqueda": busqueda,
            "formulario": formulario,
            "tecnica_editada": tecnica,
            "total": TecnicaSQA.objects.count(),
            "con_referencia": TecnicaSQA.objects.exclude(referencia_norma="").count(),
        },
    )


def lista_tecnicas(request):
    """RF-11: catálogo de técnicas SQA."""
    return _catalogo_tecnicas(request, TecnicaSQAForm())


def tecnica_nueva(request):
    """RF-11: agregar una técnica al catálogo."""
    if request.method == "POST":
        formulario = TecnicaSQAForm(request.POST)
        if formulario.is_valid():
            tecnica = formulario.save()
            messages.success(request, f"Técnica «{tecnica.nombre}» agregada al catálogo.")
            return redirect("lista_tecnicas")
    else:
        formulario = TecnicaSQAForm()
    return _catalogo_tecnicas(request, formulario)


def editar_tecnica(request, pk):
    """RF-11: editar la descripción o la referencia de una técnica del catálogo."""
    tecnica = get_object_or_404(TecnicaSQA, pk=pk)

    if request.method == "POST":
        formulario = TecnicaSQAForm(request.POST, instance=tecnica)
        if formulario.is_valid():
            tecnica = formulario.save()
            messages.success(request, f"Técnica «{tecnica.nombre}» actualizada.")
            return redirect("lista_tecnicas")
    else:
        formulario = TecnicaSQAForm(instance=tecnica)
    return _catalogo_tecnicas(request, formulario, tecnica)


def tecnicas_proyecto(request, pk):
    """RF-12: técnicas asignadas a un proyecto y formulario para asignar una nueva."""
    proyecto = get_object_or_404(Proyecto.objects.select_related("periodo", "lider"), pk=pk)

    if request.method == "POST":
        formulario = AsignacionTecnicaForm(request.POST, proyecto=proyecto)
        if formulario.is_valid():
            asignacion = formulario.save()
            messages.success(
                request,
                f"Técnica «{asignacion.tecnica}» asignada a {asignacion.usuario} "
                f"con frecuencia «{asignacion.frecuencia}».",
            )
            return redirect("tecnicas_proyecto", pk=proyecto.pk)
    else:
        formulario = AsignacionTecnicaForm(proyecto=proyecto)

    asignaciones = (
        proyecto.asignaciones_tecnicas.select_related("tecnica", "usuario")
        .annotate(registradas=Count("aplicaciones"))
        .order_by("tecnica__nombre")
    )
    return render(
        request,
        "dashboard/tecnicas_proyecto.html",
        {
            "proyecto": proyecto,
            "asignaciones": asignaciones,
            "formulario": formulario,
            "total_catalogo": TecnicaSQA.objects.count(),
            "aplicaciones": sum(a.registradas for a in asignaciones),
        },
    )


def inicio(request):
    return render(request, "dashboard/inicio.html")
