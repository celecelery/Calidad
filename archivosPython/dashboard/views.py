from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)
from .forms import (
    AsignarMetricaForm,
    CorteForm,
    FiltroProyectosForm,
    MedicionForm,
    MetricaForm,
    PeriodoForm,
    ProyectoForm,
    etiquetas_de_cortes,
)
from .models import Metrica, MetricaProyecto, Proyecto


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


def _proyecto(pk):
    return get_object_or_404(Proyecto.objects.select_related("periodo", "lider"), pk=pk)


def _pagina_mediciones(request, proyecto, form_medicion=None, form_corte=None, form_asignar=None):
    """Pestaña Mediciones (mockup «Captura de mediciones»): captura, tabla por corte y métricas.

    Cada vista que recibe un POST le pasa su formulario con errores; los demás van vacíos.
    """
    cortes = list(proyecto.cortes.all())
    metricas = list(proyecto.metricas.all())
    ultimo = cortes[-1] if cortes else None
    mediciones = {
        (m.metrica_id, m.corte_id): m
        for m in MetricaProyecto.objects.filter(proyecto=proyecto).select_related(
            "metrica", "capturado_por"
        )
    }

    if form_medicion is None:
        # Como en el mockup: se propone el último corte y la primera métrica pendiente en él.
        pendientes = [m for m in metricas if ultimo and (m.pk, ultimo.pk) not in mediciones]
        form_medicion = MedicionForm(
            proyecto=proyecto,
            initial={"corte": ultimo, "metrica": (pendientes or metricas or [None])[0]},
        )
    # Celda resaltada en la tabla: la métrica y el corte elegidos en el formulario.
    seleccion = (str(form_medicion["metrica"].value()), str(form_medicion["corte"].value()))

    filas = []
    for metrica in metricas:
        celdas = []
        for corte in cortes:
            medicion = mediciones.get((metrica.pk, corte.pk))
            celdas.append({
                "medicion": medicion,
                "cumple": metrica.cumple(medicion.valor) if medicion else None,
                "seleccionada": seleccion == (str(metrica.pk), str(corte.pk)),
            })
        ultima = mediciones.get((metrica.pk, ultimo.pk)) if ultimo else None
        filas.append({"metrica": metrica, "celdas": celdas, "ultima": ultima})

    totales = []
    for i, _corte in enumerate(cortes):
        capturadas = [fila["celdas"][i] for fila in filas if fila["celdas"][i]["medicion"]]
        totales.append({
            "cumplidas": sum(1 for celda in capturadas if celda["cumple"]),
            "capturadas": len(capturadas),
        })

    etiquetas = etiquetas_de_cortes(proyecto)
    return render(
        request,
        "dashboard/metricas_proyecto.html",
        {
            "proyecto": proyecto,
            "metricas": metricas,
            "cortes": [{"corte": c, "numero": n} for n, c in enumerate(cortes, 1)],
            "ultimo": {"corte": ultimo, "etiqueta": etiquetas.get(ultimo.pk)} if ultimo else None,
            "filas": filas,
            "totales": totales,
            "pendientes_ultimo": sum(1 for fila in filas if ultimo and not fila["ultima"]),
            "form_medicion": form_medicion,
            "form_corte": form_corte or CorteForm(proyecto=proyecto),
            "abrir_corte": form_corte is not None or not cortes,
            "form_asignar": form_asignar or AsignarMetricaForm(proyecto=proyecto),
            # Para que la línea fx y la unidad cambien al elegir otra métrica (ver plantilla).
            "detalle_metricas": {
                str(m.pk): {
                    "fx": f"{m.clave or m.nombre} = {m.formula} · Meta {m.meta_texto}"
                    + (f" · Fuente: {m.fuente}" if m.fuente else ""),
                    "unidad": "%" if m.unidad == Metrica.Unidad.PORCENTAJE else "",
                }
                for m in metricas
            },
        },
    )


def metricas_proyecto(request, pk):
    """Pestaña Mediciones del proyecto. Por POST asigna una métrica del catálogo (RF-07)."""
    proyecto = _proyecto(pk)
    if request.method != "POST":
        return _pagina_mediciones(request, proyecto)

    formulario = AsignarMetricaForm(request.POST, proyecto=proyecto)
    if not formulario.is_valid():
        return _pagina_mediciones(request, proyecto, form_asignar=formulario)
    metrica = formulario.cleaned_data["metrica"]
    proyecto.metricas.add(metrica)
    messages.success(request, f"Métrica «{metrica}» asignada a «{proyecto.nombre}».")
    return redirect("metricas_proyecto", pk=proyecto.pk)


@require_POST
def capturar_medicion(request, pk):
    """RF-08: guardar el valor de una métrica en un corte; si ya existía, se corrige."""
    proyecto = _proyecto(pk)
    formulario = MedicionForm(request.POST, proyecto=proyecto)
    if not formulario.is_valid():
        return _pagina_mediciones(request, proyecto, form_medicion=formulario)

    datos = formulario.cleaned_data
    _, creada = MetricaProyecto.objects.update_or_create(
        proyecto=proyecto,
        metrica=datos["metrica"],
        corte=datos["corte"],
        defaults={"valor": datos["valor"], "capturado_por": request.user},
    )
    etiqueta = etiquetas_de_cortes(proyecto)[datos["corte"].pk]
    accion = "guardada" if creada else "actualizada"
    messages.success(request, f"Medición de «{datos['metrica']}» en {etiqueta} {accion}.")
    return redirect("metricas_proyecto", pk=proyecto.pk)


@require_POST
def agregar_corte(request, pk):
    """RF-08: agregar un corte (fecha) al proyecto para capturar sus mediciones."""
    proyecto = _proyecto(pk)
    formulario = CorteForm(request.POST, proyecto=proyecto)
    if not formulario.is_valid():
        return _pagina_mediciones(request, proyecto, form_corte=formulario)

    corte = formulario.save()
    messages.success(request, f"{etiquetas_de_cortes(proyecto)[corte.pk]} agregado.")
    return redirect("metricas_proyecto", pk=proyecto.pk)


@require_POST
def quitar_metrica(request, pk, metrica_pk):
    """RF-07: quitar una métrica de un proyecto; no la borra del catálogo ni de otros proyectos."""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    metrica = get_object_or_404(proyecto.metricas, pk=metrica_pk)
    proyecto.metricas.remove(metrica)
    messages.success(request, f"Métrica «{metrica}» quitada de «{proyecto.nombre}».")
    return redirect("metricas_proyecto", pk=proyecto.pk)


def inicio(request):
    return render(request, "dashboard/inicio.html")
