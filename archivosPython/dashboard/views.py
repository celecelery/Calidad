from django.shortcuts import render
from archivosPython.dashboard.forms import *
from archivosPython.dashboard.forms import PeriodoForm
from .models import *

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)

# Create your views here.
def periodo_view(request):
    if request.method == "POST":
        formulario = PeriodoForm(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["nombre"]
            fecha_inicio = formulario.cleaned_data["fecha inicio"]
            fecha_fin = formulario.cleaned_data["fecha fin"]

            # Aquí puedes guardar los datos o procesarlos.
            return render(
                request,
                "formulario_periodo.html",
                {
                    "formulario": PeriodoForm(),
                    "exito": True,
                    "nombre": nombre,
                }
            )
    else:
        formulario = PeriodoForm()

    return render(
        request,
        "formulario_periodo.html",
        {"formulario": formulario}
    )

def inicio(request):
    return render(request, "dashboard/inicio.html")