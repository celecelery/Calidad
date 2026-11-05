from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("periodos/nuevo/", views.periodo_view, name="periodo_nuevo"),
    path("proyectos/nuevo/", views.proyecto_view, name="proyecto_nuevo"),
    path("proyectos/", views.lista_proyectos, name="lista_proyectos"),
    path("proyectos/<int:pk>/editar/", views.editar_proyecto, name="editar_proyecto"),
    path("proyectos/<int:pk>/metricas/", views.metricas_proyecto, name="metricas_proyecto"),
    path("proyectos/<int:pk>/mediciones/", views.capturar_medicion, name="capturar_medicion"),
    path("proyectos/<int:pk>/cortes/", views.agregar_corte, name="agregar_corte"),
    path(
        "proyectos/<int:pk>/metricas/<int:metrica_pk>/quitar/",
        views.quitar_metrica,
        name="quitar_metrica",
    ),
    path("proyectos/<int:pk>/graficas/", views.grafica_metricas, name="metricas_proyecto"),
    path("metricas/", views.metricas_view, name="lista_metricas"),
    path("metricas/nueva/", views.metricas_view, name="metrica_nueva"),
    path("metricas/<int:pk>/editar/", views.metricas_view, name="editar_metrica"),
    path("proyectos/<int:pk>/tecnicas/", views.tecnicas_proyecto, name="tecnicas_proyecto"),
    path("tecnicas/", views.lista_tecnicas, name="lista_tecnicas"),
    path("tecnicas/nueva/", views.tecnica_nueva, name="tecnica_nueva"),
    path("tecnicas/<int:pk>/editar/", views.editar_tecnica, name="editar_tecnica"),
]
