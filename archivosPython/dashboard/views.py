from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)
from .forms import FiltroProyectosForm, PeriodoForm, ProyectoForm
from .models import Proyecto


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

    return render(request, "dashboard/formulario_proyecto.html", {"formulario": formulario})


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
    proyecto = get_object_or_404(Proyecto, pk=pk)

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


def inicio(request):
    return render(request, "dashboard/inicio.html")
