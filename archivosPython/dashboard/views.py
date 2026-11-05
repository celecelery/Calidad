from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import plotly_app  # noqa: F401  (registra la aplicación Dash)
from .cumplimiento import cumplimiento_de_tecnicas
from .forms import (
    AplicacionTecnicaForm,
    AsignacionTecnicaForm,
    AsignarMetricaForm,
    CorteForm,
    CorteReporteForm,
    FiltroProyectosForm,
    MedicionForm,
    MetricaForm,
    PeriodoForm,
    ProyectoForm,
    PrsFusionadosForm,
    TecnicaSQAForm,
    etiquetas_de_cortes,
)
from .models import (
    AsignacionTecnica,
    Metrica,
    MetricaProyecto,
    Proyecto,
    ReporteSalud,
    TecnicaSQA,
    Usuario,
)
from .salud import reporte_de_salud


def obtener_perfil_usuario(request):
    if not request.user.is_authenticated:
        return None
    usuario = Usuario.objects.filter(user=request.user).first()
    return usuario.perfil if usuario else None


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
    if obtener_perfil_usuario(request) != "administrador":
        messages.error(request, "Solo un administrador puede editar proyectos.")
        return redirect("lista_proyectos")
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
        {
            "formulario": formulario,
            "proyecto": proyecto,
            # Tarjeta «Resumen» del mockup de Datos.
            "resumen": {
                "cortes": proyecto.cortes.count(),
                "metricas": proyecto.metricas.count(),
                "tecnicas": proyecto.asignaciones_tecnicas.count(),
            },
        },
    )


@require_POST
def archivar_proyecto(request, pk):
    """RF-05: archivar un proyecto sin borrarlo; sale del dashboard y del menú lateral."""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if proyecto.archivado:
        messages.info(request, f"El proyecto «{proyecto.nombre}» ya estaba archivado.")
    else:
        proyecto.archivar()
        messages.success(
            request,
            f"Proyecto «{proyecto.nombre}» archivado. Sus mediciones, técnicas y reportes "
            "se conservan.",
        )
    return redirect("lista_proyectos")


@require_POST
def reactivar_proyecto(request, pk):
    """RF-05: reactivar un proyecto archivado (vuelve al dashboard y al menú lateral)."""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if not proyecto.archivado:
        messages.info(request, f"El proyecto «{proyecto.nombre}» ya estaba activo.")
    else:
        proyecto.reactivar()
        messages.success(request, f"Proyecto «{proyecto.nombre}» reactivado.")
    return redirect("lista_proyectos")


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
    if obtener_perfil_usuario(request) != "administrador":
        messages.error(request, "Solo un administrador puede quitar métricas.")
        return redirect("metricas_proyecto", pk=pk)
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
    if obtener_perfil_usuario(request) != "administrador":
        messages.error(request, "Solo un administrador puede editar técnicas.")
        return redirect("lista_tecnicas")
    if request.method == "POST":
        formulario = TecnicaSQAForm(request.POST, instance=tecnica)
        if formulario.is_valid():
            tecnica = formulario.save()
            messages.success(request, f"Técnica «{tecnica.nombre}» actualizada.")
            return redirect("lista_tecnicas")
    else:
        formulario = TecnicaSQAForm(instance=tecnica)
    return _catalogo_tecnicas(request, formulario, tecnica)


def _pagina_tecnicas(request, proyecto, formulario=None, form_prs=None):
    """Pestaña Técnicas SQA (mockup «Técnicas del proyecto»): asignar (RF-12) y cumplimiento
    (RF-14). Cada vista que recibe un POST le pasa su formulario con errores."""
    cumplimiento = cumplimiento_de_tecnicas(proyecto)
    asignaciones = []
    for fila in cumplimiento.tecnicas:
        fila.asignacion.registradas = fila.registradas
        asignaciones.append(fila.asignacion)
    cortes = list(proyecto.cortes.all())
    hay_por_pr = any(
        t.asignacion.frecuencia == AsignacionTecnica.Frecuencia.POR_PR
        for t in cumplimiento.tecnicas
    )
    return render(
        request,
        "dashboard/tecnicas_proyecto.html",
        {
            "proyecto": proyecto,
            "cumplimiento": cumplimiento,
            # `asignaciones` (con `registradas`) y `aplicaciones` se conservan como en RF-12.
            "asignaciones": asignaciones,
            "aplicaciones": cumplimiento.registradas,
            "formulario": formulario or AsignacionTecnicaForm(proyecto=proyecto),
            "total_catalogo": TecnicaSQA.objects.count(),
            "cortes": cortes,
            "ultimo": cortes[-1] if cortes else None,
            "mostrar_prs": hay_por_pr and cortes,
            "abrir_prs": form_prs is not None,
            "form_prs": form_prs or PrsFusionadosForm(proyecto=proyecto),
        },
    )


def tecnicas_proyecto(request, pk):
    """RF-12 y RF-14: técnicas asignadas con su cumplimiento y formulario para asignar."""
    proyecto = _proyecto(pk)

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
        return _pagina_tecnicas(request, proyecto, formulario=formulario)

    return _pagina_tecnicas(request, proyecto)


@require_POST
def guardar_prs_fusionados(request, pk):
    """RF-14: PRs fusionados acumulados a un corte (esperadas de las técnicas «Por PR»)."""
    proyecto = _proyecto(pk)
    formulario = PrsFusionadosForm(request.POST, proyecto=proyecto)
    if not formulario.is_valid():
        return _pagina_tecnicas(request, proyecto, form_prs=formulario)

    corte = formulario.cleaned_data["corte"]
    corte.prs_fusionados = formulario.cleaned_data["prs_fusionados"]
    corte.save(update_fields=["prs_fusionados"])
    etiqueta = etiquetas_de_cortes(proyecto)[corte.pk]
    messages.success(request, f"PRs fusionados al {etiqueta}: {corte.prs_fusionados}.")
    return redirect("tecnicas_proyecto", pk=proyecto.pk)


def _corte_de(fecha, cortes):
    """Corte al que cuenta una aplicación: el primero con fecha igual o posterior."""
    for numero, corte in enumerate(cortes, 1):
        if fecha <= corte.fecha:
            return f"Corte {numero}"
    return "Después del último corte"


def registrar_aplicacion(request, pk):
    """RF-13: registrar la aplicación de una técnica; no se guarda sin enlace de evidencia."""
    proyecto = _proyecto(pk)

    if request.method == "POST":
        formulario = AplicacionTecnicaForm(request.POST, proyecto=proyecto)
        if formulario.is_valid():
            aplicacion = formulario.save()
            fila = next(
                t
                for t in cumplimiento_de_tecnicas(proyecto).tecnicas
                if t.asignacion.pk == aplicacion.asignacion_id
            )
            avance = (
                f" Lleva {fila.registradas} de {fila.esperadas} ({fila.porcentaje:.0f} %)."
                if fila.porcentaje is not None
                else ""
            )
            messages.success(
                request,
                f"Aplicación de «{aplicacion.asignacion.tecnica}» registrada.{avance}",
            )
            return redirect("tecnicas_proyecto", pk=proyecto.pk)
        seleccionada = formulario.cleaned_data.get("asignacion")
    else:
        seleccionada = None
        if request.GET.get("asignacion", "").isdigit():
            seleccionada = proyecto.asignaciones_tecnicas.filter(
                pk=request.GET["asignacion"]
            ).first()
        formulario = AplicacionTecnicaForm(
            proyecto=proyecto, initial={"asignacion": seleccionada} if seleccionada else None
        )

    # Panel lateral del mockup: la técnica elegida y sus aplicaciones registradas.
    detalle = None
    if seleccionada is not None:
        cortes = list(proyecto.cortes.all())
        fila = next(
            t
            for t in cumplimiento_de_tecnicas(proyecto).tecnicas
            if t.asignacion.pk == seleccionada.pk
        )
        detalle = {
            "fila": fila,
            "aplicaciones": [
                {"aplicacion": a, "corte": _corte_de(a.fecha, cortes)}
                for a in fila.aplicaciones
            ],
        }

    errores = formulario.errors if formulario.is_bound else {}
    return render(
        request,
        "dashboard/registrar_aplicacion.html",
        {
            "proyecto": proyecto,
            "formulario": formulario,
            "detalle": detalle,
            "falta_evidencia": "evidencia" in errores and not formulario.data.get("evidencia"),
        },
    )
def grafica_metricas(request, pk):
    """RF-09: Graficas por métrica"""
    proyecto = _proyecto(pk) 
    mediciones = (
        MetricaProyecto.objects
        .filter(proyecto=proyecto)
        .select_related("metrica", "corte")
        .order_by("-metrica__es_base", "metrica__clave", "metrica__nombre", "corte__fecha")
    )

    agrupadas = {}
    for m in mediciones:
        metrica = m.metrica
        grupo = agrupadas.setdefault(metrica.pk, {
            "nombre": str(metrica),
            "es_porcentaje": metrica.unidad == metrica.Unidad.PORCENTAJE,
            "meta": float(metrica.meta),
            "meta_texto": metrica.meta_texto,
            "cortes": [],
            "valores": [],
            "cumple": [],
        })
        grupo["cortes"].append(str(m.corte))
        grupo["valores"].append(float(m.valor))
        grupo["cumple"].append(metrica.cumple(m.valor))

    return render(request, "dashboard/proyecto_grafica.html", {
        "proyecto": proyecto,
        "graficas": list(agrupadas.values()),
    })


def reporte_salud(request, pk):
    """RF-15: reporte de salud de un proyecto en un corte (por omisión, el último)."""
    proyecto = _proyecto(pk)
    selector = CorteReporteForm(request.GET or None, proyecto=proyecto)
    corte = None
    if request.GET and selector.is_valid():
        corte = selector.cleaned_data["corte"]
    if corte is None:
        corte = proyecto.cortes.last()
        selector = CorteReporteForm(proyecto=proyecto, initial={"corte": corte})

    reporte = reporte_de_salud(proyecto, corte) if corte else None
    return render(
        request,
        "dashboard/reporte_salud.html",
        {"proyecto": proyecto, "selector": selector, "reporte": reporte},
    )


def inicio(request):
    proyectos = Proyecto.objects.all()
    reportes = ReporteSalud.objects.filter(proyecto__in=proyectos).select_related("proyecto")
    return render(request, "dashboard/inicio.html", {
        "proyectos": proyectos,
        "reportes": reportes,
    })
