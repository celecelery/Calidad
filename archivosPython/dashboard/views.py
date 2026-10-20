from django.contrib import messages
from django.shortcuts import redirect, render

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)
from .forms import PeriodoForm, ProyectoForm


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


def inicio(request):
    return render(request, "dashboard/inicio.html")
