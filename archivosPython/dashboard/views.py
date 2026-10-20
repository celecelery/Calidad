from django.shortcuts import render

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)

# Create your views here.


def inicio(request):
    return render(request, "dashboard/inicio.html")