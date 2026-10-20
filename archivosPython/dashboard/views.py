from django.shortcuts import render
from . import plotly_app  # Registra la aplicación Dash
# Create your views here.


def inicio(request):
    return render(request, "dashboard/inicio.html")