#pip install dash

import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# Inicializar la aplicación Dash
app = dash.Dash(__name__)
app.title = "Monitoreo de Flota de Vehículos"

# Datos ficticios
indicadores = {
    "Total de Alertas": 120,
    "Alertas Críticas": 35,
    "Vehículos en Buen Estado": 85
}

clasificacion_alertas = {
    "Críticas 🔴": 35,
    "Moderadas 🟠": 50,
    "Leves 🟢": 35
}

acciones_correctivas = {
    "🚧 Acción Pendiente": 40,
    "🔄 En Proceso": 50,
    "✅ Resuelto": 30
}

# Gráfico de clasificación de alertas
fig_alertas = go.Figure()
fig_alertas.add_trace(go.Bar(
    x=list(clasificacion_alertas.keys()),
    y=list(clasificacion_alertas.values()),
    marker=dict(color=["red", "orange", "green"])
))
fig_alertas.update_layout(title="Clasificación de Alertas", template="plotly_dark")

# Gráfico de estado de acciones correctivas
fig_acciones = go.Figure()
fig_acciones.add_trace(go.Pie(
    labels=list(acciones_correctivas.keys()),
    values=list(acciones_correctivas.values()),
    hole=0.4
))
fig_acciones.update_layout(title="Estado de Acciones Correctivas", template="plotly_dark")

# Diseño de la app
app.layout = html.Div(style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '20px'}, children=[
    
    html.H1("🚛 Monitoreo en Tiempo Real - Flota de Vehículos", style={'textAlign': 'center'}),
    
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '50px'}, children=[
        html.Div(style={'border': '1px solid white', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H3("📊 Total de Alertas"),
            html.H2(f"{indicadores['Total de Alertas']}", style={'color': 'yellow'})
        ]),
        html.Div(style={'border': '1px solid white', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H3("🔴 Alertas Críticas"),
            html.H2(f"{indicadores['Alertas Críticas']}", style={'color': 'red'})
        ]),
        html.Div(style={'border': '1px solid white', 'padding': '20px', 'borderRadius': '10px'}, children=[
            html.H3("✅ Vehículos en Buen Estado"),
            html.H2(f"{indicadores['Vehículos en Buen Estado']}", style={'color': 'green'})
        ])
    ]),

    html.Br(),

    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '50px'}, children=[
        dcc.Graph(figure=fig_alertas, style={'width': '45%'}),
        dcc.Graph(figure=fig_acciones, style={'width': '45%'})
    ])
])

# Ejecutar el servidor
if __name__ == "__main__":
    app.run_server(debug=True)