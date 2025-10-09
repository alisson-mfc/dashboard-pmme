# dashboard_app.py
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import base64
import os

# ============================================================================
# CARREGAR DADOS PÚBLICOS E RESULTADOS
# ============================================================================
PASTA_NUVENS = 'nuvens_palavras'

with open('dados_publicos.json', 'r', encoding='utf-8') as f:
    dados_publicos = json.load(f)['dashboard']

try:
    with open('resultados_analises.json', 'r', encoding='utf-8') as f:
        RESULTADOS_ANALISES = json.load(f)
except FileNotFoundError:
    print("AVISO: 'resultados_analises.json' não encontrado. Parte qualitativa do dashboard estará vazia.")
    RESULTADOS_ANALISES = None

# ============================================================================
# FUNÇÕES DE CRIAÇÃO DE GRÁFICOS
# ============================================================================

TOTAL_REGISTROS = len(dados_publicos.get('idade', []))

def criar_grafico_barras(dados_dict, titulo, height=450):
    if not dados_dict: return go.Figure().update_layout(title=f"{titulo} (Sem dados)")
    df_contagem = pd.DataFrame(list(dados_dict.items()), columns=['Categoria', 'Quantidade']).sort_values('Quantidade', ascending=False)
    if len(df_contagem) > 25:
        df_contagem = df_contagem.head(25)
    
    # Recalcula o total apenas para as categorias mostradas para a porcentagem fazer sentido no gráfico
    total_parcial = df_contagem['Quantidade'].sum()
    percentual = (df_contagem['Quantidade'] / total_parcial * 100).round(1)

    fig = go.Figure(data=[go.Bar(
        x=df_contagem['Categoria'], y=df_contagem['Quantidade'],
        text=[f'{p}%' for p in percentual], textposition='outside',
        marker_color='#1f77b4'
    )])
    max_valor = df_contagem['Quantidade'].max()
    fig.update_layout(title=titulo, template='plotly_white', height=height,
                      margin=dict(t=80, b=60, l=60, r=40),
                      yaxis=dict(range=[0, max_valor * 1.25]))
    return fig

def criar_histograma(dados_list, titulo):
    if not dados_list: return go.Figure().update_layout(title=f"{titulo} (Sem dados)")
    s_dados = pd.Series(dados_list)
    fig = go.Figure(data=[go.Histogram(x=s_dados, marker_color='#2ca02c', nbinsx=20)])
    media, mediana = s_dados.mean(), s_dados.median()
    fig.add_vline(x=media, line_dash="dash", line_color="red", annotation_text=f"Média: {media:.1f}", annotation_position="top right")
    fig.add_vline(x=mediana, line_dash="dash", line_color="blue", annotation_text=f"Mediana: {mediana:.1f}", annotation_position="top left")
    fig.update_layout(title=titulo, template='plotly_white', height=450, margin=dict(t=80, b=60, l=60, r=40))
    return fig

def criar_grafico_regioes(dados_list):
    if not dados_list: return go.Figure().update_layout(title="Distribuição Regional (Sem dados)")
    df_regioes = pd.DataFrame(dados_list)
    fig = px.line(df_regioes, x='Momento', y='Quantidade', color='Região', markers=True, title='Distribuição Regional por Momento')
    fig.update_layout(template='plotly_white', height=550, margin=dict(t=80, b=60, l=60, r=40))
    return fig

# ============================================================================
# LAYOUT E CALLBACKS
# ============================================================================

# Opções do Dropdown para reutilização no layout e no callback
dropdown_apropriacao_options = [
    {'label': 'Organização de Redes de Atenção à Saúde', 'value': 'apropriacao_redes'},
    {'label': 'Coordenação do Cuidado', 'value': 'apropriacao_coordenacao'},
    {'label': 'Gestão da Clínica e do Cuidado', 'value': 'apropriacao_gestao'},
    {'label': 'Saúde Baseada em Evidências', 'value': 'apropriacao_evidencias'},
    {'label': 'Plataformas Digitais', 'value': 'experiencia_digital'},
]

def create_layout():
    """Cria e retorna o layout do dashboard."""
    layout = html.Div([
        html.H1('Dashboard PMM-e - Visão Geral', style={'textAlign': 'center', 'marginBottom': '30px'}),

        html.H2('Dados Pessoais', className="mt-5"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['raca_ds'], 'Distribuição por Raça')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['sexo_ds'], 'Distribuição por Sexo')), className="col-md-6"),
        ], className="row"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_histograma(dados_publicos['idade'], 'Distribuição de Idade')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['estado_civil_ds'], 'Estado Civil')), className="col-md-6"),
        ], className="row mt-4"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['ident_genero_ds'], 'Identidade de Gênero')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['orientacao_sexual_ds'], 'Orientação Sexual')), className="col-md-6"),
        ], className="row mt-4"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['tem_nome_social'], 'Profissionais com Nome Social')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['aa_tipo_ds'], 'Ações Afirmativas')), className="col-md-6"),
        ], className="row mt-4"),

        html.H2('Formação Acadêmica', className="mt-5"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_histograma(dados_publicos['tempo_graduado'], 'Tempo de Graduado (anos)')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['pais_formacao_ds'], 'País de Formação')), className="col-md-6"),
        ], className="row"),

        html.H2('Especialidades e Títulos', className="mt-5"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['rm_rec_cnrm_ds'], 'Residências Médicas')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['tit_esp_amb_ds'], 'Título de Especialista')), className="col-md-6"),
        ], className="row mt-4"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['rm_1_esp_medica_ds'], 'Área - RM Primária')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['rm_2_esp_medica_ds'], 'Área - RM Secundária')), className="col-md-6"),
        ], className="row mt-4"),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['amb_1_esp_medica_ds'], 'Área - Título Especialista Primário')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['amb_2_esp_medica_ds'], 'Área - Título Especialista Secundário')), className="col-md-6"),
        ], className="row mt-4"),
        html.Div([
             dcc.Graph(figure=criar_grafico_barras(dados_publicos['curso_nome_limpo'], 'Cursos de Aprimoramento (Top 25)', height=550))
        ], className="row mt-4"),
        
        html.H2('Distribuição Geográfica', className="mt-5"),
        dcc.Graph(figure=criar_grafico_regioes(dados_publicos['fluxo_regional'])),
        html.Div([
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['regiao_nascimento'], 'Região de Nascimento')), className="col-md-6"),
            html.Div(dcc.Graph(figure=criar_grafico_barras(dados_publicos['regiao_vaga'], 'Região da Vaga Principal')), className="col-md-6"),
        ], className="row mt-4"),
        
        # ===== SEÇÃO ADICIONADA AQUI =====
        html.Div([
            html.H2('Apropriação sobre Temas', className="mt-5"),
            html.Label('Selecione o tema:', style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='dropdown-apropriacao',
                options=dropdown_apropriacao_options,
                value='apropriacao_redes',
                clearable=False,
                style={'marginBottom': 20}
            ),
            dcc.Graph(id='grafico-apropriacao'),
        ], style={'marginBottom': 50}),
        # ==================================
        
        html.H2('Análise Qualitativa', className="mt-5"),
        dcc.Dropdown(
            id='dropdown-qualitativo',
            options=[
                {'label': 'Expectativas em relação ao PMM-e', 'value': 'aptidoes_rotina'},
                {'label': 'Considera apto para atuação', 'value': 'competencias_fortalecer'},
                {'label': 'Impressão sobre o serviço', 'value': 'impressao_servico'},
                {'label': 'Expectativas para imersão', 'value': 'momento_imersao'},
            ],
            value='aptidoes_rotina',
        ),
        html.Div([
            html.H3('Nuvem de Palavras', className="mt-4 text-center"),
            html.Img(id='nuvem-palavras', style={'maxWidth': '800px', 'width': '100%', 'margin': 'auto', 'display': 'block'}),
        ], className="mt-4"),
        html.Div([
            html.H3('Análise de Sentimentos', className="mt-4 text-center"),
            dcc.Graph(id='grafico-sentimentos'),
        ], className="mt-4"),
        html.H3('Resumo dos Textos', className="mt-4"),
        html.Div(id='resumo-textos', style={'padding': 20, 'backgroundColor': '#f8f9fa', 'borderRadius': 5, 'border': '1px solid #dee2e6'}),
    ])
    return layout

def register_callbacks(app):
    """Registra todos os callbacks do dashboard."""

    # ===== CALLBACK ADICIONADO AQUI =====
    @app.callback(
        Output('grafico-apropriacao', 'figure'),
        Input('dropdown-apropriacao', 'value')
    )
    def atualizar_apropriacao(tema_selecionado):
        dados_tema = dados_publicos[tema_selecionado]
        
        # Mapeia as chaves (ex: 'A') para rótulos mais descritivos (ex: 'Maior (A)')
        mapeamento = {'A': 'Maior (A)', 'E': 'Menor (E)'}
        dados_mapeados = {mapeamento.get(k, 'Não Avaliado'): v for k, v in dados_tema.items()}

        # Cria um mapa de valor para rótulo para obter o título completo
        options_map = {opt['value']: opt['label'] for opt in dropdown_apropriacao_options}
        titulo_grafico = options_map[tema_selecionado]

        return criar_grafico_barras(dados_mapeados, titulo_grafico)
    # ====================================

    @app.callback(
        [Output('nuvem-palavras', 'src'),
         Output('grafico-sentimentos', 'figure'),
         Output('resumo-textos', 'children')],
        Input('dropdown-qualitativo', 'value')
    )
    def atualizar_qualitativo(coluna):
        if RESULTADOS_ANALISES is None or coluna not in RESULTADOS_ANALISES.get('campos', {}):
            fig_vazia = go.Figure().update_layout(title="Dados não disponíveis")
            return '', fig_vazia, "Dados não disponíveis. Execute o script de pré-processamento de análises."

        dados_campo = RESULTADOS_ANALISES['campos'][coluna]
        # Nuvem de Palavras
        img_src = ''
        arquivo_nuvem = dados_campo.get('nuvem_palavras')
        if arquivo_nuvem and os.path.exists(arquivo_nuvem):
            with open(arquivo_nuvem, 'rb') as img_file:
                img_src = f'data:image/png;base64,{base64.b64encode(img_file.read()).decode()}'
        
        # Gráfico de Sentimentos
        dist = dados_campo['sentimentos']['distribuicao']
        
        color_map = {
            'Positivo': '#28a745',
            'Neutro': '#ffc107',
            'Negativo': '#dc3545'
        }

        df_sent = pd.DataFrame(list(dist.items()), columns=['Sentimento', 'Quantidade'])
        
        fig_sent = px.bar(
            df_sent,
            x='Sentimento', 
            y='Quantidade', 
            color='Sentimento',
            color_discrete_map=color_map,
            title='Análise de Sentimentos', 
            labels={'Sentimento': 'Sentimento', 'Quantidade': 'Quantidade'}
        )
        fig_sent.update_layout(template='plotly_white', showlegend=False)
        
        # Resumo
        resumo = dados_campo.get('resumo', 'Resumo não disponível.')
        
        return img_src, fig_sent, resumo