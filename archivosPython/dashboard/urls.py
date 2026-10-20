from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("periodos/nuevo/", views.periodo_view, name="periodo_nuevo"),
    path("proyectos/nuevo/", views.proyecto_view, name="proyecto_nuevo"),
]
