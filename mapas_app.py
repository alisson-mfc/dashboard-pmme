# mapas_app.py
import json
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback_context
import requests

# ============================================================================
# CONFIG E CARREGAMENTO DE DADOS
# ============================================================================

with open('dados_publicos.json', 'r', encoding='utf-8') as f:
    dados_mapas = json.load(f)['mapas']

GEOJSON_CACHE = {}
ESTADOS_SIGLAS = {'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR', 'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'}
SIGLAS_IBGE = {'AC': '12', 'AM': '13', 'AP': '16', 'PA': '15', 'RO': '11', 'RR': '14', 'TO': '17', 'AL': '27', 'BA': '29', 'CE': '23', 'MA': '21', 'PB': '25', 'PE': '26', 'PI': '22', 'RN': '24', 'SE': '28', 'ES': '32', 'MG': '31', 'RJ': '33', 'SP': '35', 'PR': '41', 'RS': '43', 'SC': '42', 'DF': '53', 'GO': '52', 'MT': '51', 'MS': '50'}

def carregar_geojson(url):
    if url in GEOJSON_CACHE:
        return GEOJSON_CACHE[url]
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        geojson = response.json()
        GEOJSON_CACHE[url] = geojson
        return geojson
    except Exception as e:
        print(f"Erro ao carregar GeoJSON de {url}: {e}")
        return None

# ============================================================================
# FUNÇÕES DE CRIAÇÃO DE MAPAS
# ============================================================================

# ===== CORREÇÃO DEFINITIVA APLICADA AQUI =====
def criar_mapa_calor_estados(dados_dict, titulo):
    url_brasil = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    geojson_br = carregar_geojson(url_brasil)
    if not geojson_br:
        return go.Figure().update_layout(title="Erro ao carregar GeoJSON do Brasil")

    data_lookup = dados_dict
    locations = []
    z_values = []
    
    # Encontra o valor máximo para criar a escala de cores
    max_val = max(data_lookup.values()) if data_lookup else 1

    for feature in geojson_br['features']:
        state_name = feature['properties']['name']
        locations.append(state_name)
        # Pega o valor do dicionário; se não encontrar, atribui 0
        value = data_lookup.get(state_name, 0)
        z_values.append(value)

    # Cria uma escala de cores personalizada.
    # O ponto de quebra é um número muito pequeno para garantir que '0' tenha sua própria cor
    # e o gradiente azul comece imediatamente para valores >= 1.
    break_point = 0.000001
    
    colorscale = [
        [0.0, "#E0E0E0"],           # Cor cinza para o valor 0
        [break_point, "#dbe9f6"],   # Início do gradiente azul (azul claro)
        [1.0, "#0d559f"]            # Fim do gradiente azul (azul escuro)
    ]

    fig = go.Figure(go.Choropleth(
        geojson=geojson_br,
        locations=locations,
        z=z_values,
        featureidkey="properties.name",
        colorscale=colorscale, # Usa a escala de cores personalizada
        colorbar_title_text="Profissionais",
        marker_line_color='black',
        marker_line_width=0.5
    ))
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=titulo, height=600, margin=dict(l=0, r=0, t=50, b=0), template='plotly_white')
    
    return fig


def criar_mapa_municipios_estado(sigla_estado):
    nome_estado_map = {v: k for k, v in ESTADOS_SIGLAS.items()}
    estado_nome = nome_estado_map.get(sigla_estado)
    codigo_ibge = SIGLAS_IBGE.get(sigla_estado)
    if not estado_nome or not codigo_ibge:
        return go.Figure().update_layout(title=f"Sigla de estado inválida: {sigla_estado}")

    url = f'https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-{codigo_ibge}-mun.json'
    geojson_estado = carregar_geojson(url)

    if not geojson_estado:
        return go.Figure().update_layout(title=f"Não foi possível carregar o mapa de {estado_nome}")

    df_vagas_municipio = pd.DataFrame(dados_mapas['vagas_por_municipio'])
    df_estado_vagas = df_vagas_municipio[df_vagas_municipio['vaga_uf'] == estado_nome]
    
    vagas_por_municipio = {row['vaga_municipio']: row['curso_nome_limpo'] for index, row in df_estado_vagas.iterrows()}

    locations = []
    z_values = []
    hover_text = []

    for feature in geojson_estado['features']:
        nome_municipio = feature['properties']['name']
        locations.append(nome_municipio)

        if nome_municipio in vagas_por_municipio:
            z_values.append(1)
            cursos = vagas_por_municipio[nome_municipio]
            cursos_html = "<br>".join([f"• {c}" for c in cursos])
            hover_text.append(f"<b>{nome_municipio}</b><br>--- Áreas ---<br>{cursos_html}")
        else:
            z_values.append(0)
            hover_text.append(f"<b>{nome_municipio}</b><br>Sem vagas")
            
    fig = go.Figure(go.Choropleth(
        geojson=geojson_estado,
        locations=locations,
        z=z_values,
        featureidkey="properties.name",
        colorscale=[[0, '#e0e0e0'], [1, '#28a745']],
        showscale=False,
        text=hover_text,
        hoverinfo='text'
    ))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title=f'Municípios com Vagas - {estado_nome}',
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        template='plotly_white'
    )
    return fig

# ============================================================================
# LAYOUT E CALLBACKS
# ============================================================================

def create_layout():
    """Cria e retorna o layout dos mapas."""
    layout = html.Div([
        html.H1('Análise Geográfica - PMM-e', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='dropdown-tipo-mapa',
            options=[
                {'label': 'Estado de Nascimento', 'value': 'rg_uf_ds'},
                {'label': 'Estado de Graduação', 'value': 'estado_graduacao'},
                {'label': 'Estado do CRM', 'value': 'uf_crm_ds'},
                {'label': 'Estado da Vaga Principal', 'value': 'vaga_uf'},
            ],
            value='vaga_uf',
            className="mb-4"
        ),
        dcc.Loading(dcc.Graph(id='mapa-principal')),
        html.Div(id='container-municipios', className="mt-4")
    ])
    return layout

def register_callbacks(app):
    """Registra todos os callbacks dos mapas."""
    @app.callback(
        Output('mapa-principal', 'figure'),
        Input('dropdown-tipo-mapa', 'value')
    )
    def atualizar_mapa_principal(coluna):
        titulos = {
            'rg_uf_ds': 'Estado de Nascimento dos Profissionais',
            'estado_graduacao': 'Estado de Graduação dos Profissionais',
            'uf_crm_ds': 'Estado do CRM dos Profissionais',
            'vaga_uf': 'Estado da Vaga Principal'
        }
        return criar_mapa_calor_estados(dados_mapas[coluna], titulos[coluna])

    @app.callback(
        Output('container-municipios', 'children'),
        [Input('mapa-principal', 'clickData'),
         Input('dropdown-tipo-mapa', 'value')]
    )
    def atualizar_mapa_municipios(clickData, tipo_mapa):
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'initial_load'

        hint_text = html.P(
            "Dica: Selecione 'Estado da Vaga Principal' e clique em um estado para ver os municípios.", 
            className="text-center text-muted mt-3"
        )
        
        if trigger_id == 'mapa-principal' and tipo_mapa == 'vaga_uf' and clickData:
            estado_nome = clickData['points'][0]['location']
            sigla_estado = ESTADOS_SIGLAS.get(estado_nome)
            if not sigla_estado:
                return html.P("Estado não reconhecido.")

            return dcc.Loading(dcc.Graph(figure=criar_mapa_municipios_estado(sigla_estado)))
        
        return hint_text