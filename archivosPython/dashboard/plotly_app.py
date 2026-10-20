import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html
from django_plotly_dash import DjangoDash

# Crear la aplicación Dash
app = DjangoDash("MiDashboard")


# Datos de ejemplo
df = pd.DataFrame({
    "Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo"],
    "Ventas": [120, 180, 150, 240, 300],
    "Gastos": [80, 100, 120, 140, 160],
})

app.layout = html.Div([
    html.H2("Dashboard de ventas"),

    dcc.Dropdown(
        id="selector",
        options=[
            {"label": "Ventas", "value": "Ventas"},
            {"label": "Gastos", "value": "Gastos"},
        ],
        value="Ventas",
        clearable=False,
    ),

    dcc.Graph(id="grafica"),
])


@app.callback(
    Output("grafica", "figure"),
    Input("selector", "value"),
)
def actualizar_grafica(variable):
    fig = px.line(
        df,
        x="Mes",
        y=variable,
        markers=True,
        title=f"{variable} por mes",
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Mes",
        yaxis_title="Importe",
    )

    return fig