from django.shortcuts import render

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)
from .forms import PeriodoForm


def periodo_view(request):
    if request.method == "POST":
        formulario = PeriodoForm(request.POST)
        if formulario.is_valid():
            periodo = formulario.save()
            return render(
                request,
                "formulario_periodo.html",
                {
                    "formulario": PeriodoForm(),
                    "exito": True,
                    "nombre": periodo.nombre,
                },
            )
    else:
        formulario = PeriodoForm()

    return render(
        request,
        "formulario_periodo.html",
        {"formulario": formulario},
    )


def inicio(request):
    return render(request, "dashboard/inicio.html")