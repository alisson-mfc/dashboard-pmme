# app_principal.py
from dash import Dash, dcc, html, Input, Output

# Importe os módulos das suas páginas
import dashboard_app
import mapas_app

# Use um tema externo para um visual mais moderno
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])
server = app.server # Exposto para o servidor de produção (Gunicorn)
app.title = "Análise PMM-e"

# Layout principal com a barra de navegação e o contêiner da página
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Cabeçalho/Navegação Fixo no Topo
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Visão Geral (Dashboard)", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("Análise Geográfica (Mapas)", href="/mapas")),
        ],
        brand="Análise PMM-e",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4" # Adiciona uma margem abaixo
    ),

    # O conteúdo da página será renderizado aqui dentro de um container
    dbc.Container(id='page-content', fluid=True)
])

# Callback para alternar entre as páginas
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard_app.create_layout()
    elif pathname == '/mapas':
        return mapas_app.create_layout()
    else:
        # Página inicial
        # ===== CORREÇÃO APLICADA AQUI =====
        # O dbc.Jumbotron foi substituído por um html.Div estilizado,
        # pois foi removido em versões mais recentes do dash-bootstrap-components.
        return dbc.Container(
            html.Div(
                [
                    html.H1("Painel de Análise do PMM-e", className="display-3"),
                    html.P(
                        "Utilize o menu de navegação acima para explorar as visualizações.",
                        className="lead",
                    ),
                    html.Hr(className="my-2"),
                    html.P("Selecione 'Visão Geral' para um dashboard descritivo ou 'Análise Geográfica' para os mapas interativos."),
                    html.Br(),
                    html.P([
                        "Álisson Oliveira dos Santos",
                        html.Br(),
                        "Universidade Aberta do SUS (UNA-SUS) • 2025"
                    ],
                        style={
                            'fontSize': '14px',
                            'textAlign': 'right',
                            'color': '#555',  
                        }
                    ),
                ],
                className="p-5 mb-4 bg-light rounded-3",
            ),
            className="mt-5",
        )

# Registre os callbacks de ambas as aplicações
# É crucial fazer isso aqui, no arquivo principal
dashboard_app.register_callbacks(app)
mapas_app.register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8051)