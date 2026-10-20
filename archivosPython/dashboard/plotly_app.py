import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from django.db.models import Count
from django_plotly_dash import DjangoDash

from .models import Proyecto

# Aplicación Dash del panel de inicio.
# Por ahora muestra proyectos por periodo con datos reales de la base de datos;
# el dashboard con el semáforo de cada proyecto (RF-09 y RF-10) es la tarea 7.3.
app = DjangoDash("MiDashboard")

COLORES_ESTADO = {"Activo": "#2563eb", "Archivado": "#94a3b8"}

app.layout = html.Div(
    [
        html.H2("Proyectos registrados por periodo"),
        html.Label("Mostrar", htmlFor="estado"),
        dcc.Dropdown(
            id="estado",
            options=[
                {"label": "Todos los proyectos", "value": "todos"},
                {"label": "Solo activos", "value": "Activo"},
                {"label": "Solo archivados", "value": "Archivado"},
            ],
            value="todos",
            clearable=False,
        ),
        dcc.Graph(id="grafica"),
    ],
    style={"fontFamily": "Arial, sans-serif"},
)


def proyectos_por_periodo(estado="todos"):
    """Cuenta los proyectos de cada periodo, separados por estado."""
    proyectos = Proyecto.objects.all()
    if estado != "todos":
        proyectos = proyectos.filter(estado=estado)

    filas = (
        proyectos.values("periodo__nombre", "periodo__fecha_inicio", "estado")
        .annotate(total=Count("pk"))
        .order_by("periodo__fecha_inicio", "estado")
    )
    return [
        {"Periodo": fila["periodo__nombre"], "Estado": fila["estado"], "Proyectos": fila["total"]}
        for fila in filas
    ]


@app.callback(
    Output("grafica", "figure"),
    Input("estado", "value"),
)
def actualizar_grafica(estado):
    datos = proyectos_por_periodo(estado)

    if not datos:
        figura = go.Figure()
        figura.add_annotation(
            text="Aún no hay proyectos registrados.",
            showarrow=False,
            font={"size": 16},
        )
        figura.update_layout(
            template="plotly_white",
            xaxis={"visible": False},
            yaxis={"visible": False},
        )
        return figura

    figura = px.bar(
        datos,
        x="Periodo",
        y="Proyectos",
        color="Estado",
        color_discrete_map=COLORES_ESTADO,
        barmode="stack",
        text_auto=True,
    )
    figura.update_layout(
        template="plotly_white",
        xaxis_title="Periodo",
        yaxis_title="Número de proyectos",
        yaxis={"dtick": 1},
        legend_title="Estado",
    )
    return figura
