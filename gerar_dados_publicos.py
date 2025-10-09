# gerar_dados_publicos.py
import json
import pandas as pd
import re
from datetime import datetime

# ============================================================================
# COPIE AS FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO DO SEU SCRIPT ORIGINAL
# É mais seguro isolá-las aqui do que importar dos scripts do Dash.
# ============================================================================

ARQUIVO_JSON = 'dados_anonimizados.json'
SIGLAS_ESTADOS = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}
REGIOES_BRASIL = {
    'Acre': 'Norte', 'Amazonas': 'Norte', 'Amapá': 'Norte', 'Pará': 'Norte',
    'Rondônia': 'Norte', 'Roraima': 'Norte', 'Tocantins': 'Norte',
    'Alagoas': 'Nordeste', 'Bahia': 'Nordeste', 'Ceará': 'Nordeste',
    'Maranhão': 'Nordeste', 'Paraíba': 'Nordeste', 'Pernambuco': 'Nordeste',
    'Piauí': 'Nordeste', 'Rio Grande do Norte': 'Nordeste', 'Sergipe': 'Nordeste',
    'Espírito Santo': 'Sudeste', 'Minas Gerais': 'Sudeste',
    'Rio de Janeiro': 'Sudeste', 'São Paulo': 'Sudeste',
    'Paraná': 'Sul', 'Rio Grande do Sul': 'Sul', 'Santa Catarina': 'Sul',
    'Distrito Federal': 'Centro-Oeste', 'Goiás': 'Centro-Oeste',
    'Mato Grosso': 'Centro-Oeste', 'Mato Grosso do Sul': 'Centro-Oeste'
}


def carregar_dados_completos():
    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = []
    for record in data['RECORDS']:
        flat_record = {'id': record['id']}
        if record.get('info_pessoais'):
            info = json.loads(record['info_pessoais'])
            flat_record.update({k: info.get(k) for k in ['raca_ds', 'data_nascimento', 'sexo_ds', 'estado_civil_ds', 'ident_genero_ds', 'orientacao_sexual_ds', 'nome_social', 'rg_uf_ds', 'municipio']})
        if record.get('formacao_academica'):
            formacao = json.loads(record['formacao_academica'])
            flat_record.update({k: formacao.get(k) for k in ['data_formacao', 'pais_formacao_ds', 'municipio_formacao', 'uf_crm_ds']})
        if record.get('listas_selecao'):
            listas = json.loads(record['listas_selecao'])
            flat_record.update({k: listas.get(k) for k in ['aa_tipo_ds', 'rm_rec_cnrm_ds', 'rm_1_esp_medica_ds', 'rm_2_esp_medica_ds', 'tit_esp_amb_ds', 'amb_1_esp_medica_ds', 'amb_2_esp_medica_ds']})
            if listas.get('vaga_principal_jdata'):
                vaga = listas['vaga_principal_jdata']
                flat_record['curso_nome'] = vaga.get('curso.nome')
                flat_record['vaga_uf'] = vaga.get('ibge.no_uf')
                flat_record['vaga_municipio'] = vaga.get('ibge.no_municipio')
        flat_record.update({k: record.get(k) for k in ['apropriacao_redes', 'apropriacao_coordenacao', 'apropriacao_gestao', 'apropriacao_evidencias']})
        flat_record['experiencia_digital'] = record.get('apropriacao_economia')
        records.append(flat_record)
    return pd.DataFrame(records)

def calcular_idade(data_nascimento):
    if pd.isna(data_nascimento): return None
    try:
        nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d')
        hoje = datetime.now()
        return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    except: return None

def calcular_tempo_graduado(data_formacao):
    if pd.isna(data_formacao): return None
    try:
        formacao = datetime.strptime(data_formacao, '%Y-%m-%d')
        hoje = datetime.now()
        return hoje.year - formacao.year - ((hoje.month, hoje.day) < (formacao.month, formacao.day))
    except: return None

def extrair_estado_municipio(municipio_formacao):
    if pd.isna(municipio_formacao): return None
    try:
        sigla = municipio_formacao.split(' - ')[1].strip()
        return SIGLAS_ESTADOS.get(sigla)
    except: return None

def limpar_nome_curso(nome):
    if pd.isna(nome): return nome
    return re.sub(r'^\d+\.\s*Aprimoramento em\s+', '', str(nome))

# ============================================================================
# SCRIPT PRINCIPAL DE GERAÇÃO DE DADOS
# ============================================================================

print("🔄 Carregando e processando dados sensíveis localmente...")
df = carregar_dados_completos()

# Aplicar transformações
df['idade'] = df['data_nascimento'].apply(calcular_idade)
df['tempo_graduado'] = df['data_formacao'].apply(calcular_tempo_graduado)
df['tem_nome_social'] = df['nome_social'].apply(lambda x: 'Sim' if pd.notna(x) and str(x).strip() else 'Não')
df['estado_graduacao'] = df['municipio_formacao'].apply(extrair_estado_municipio)
df['sexo_ds'] = df['sexo_ds'].replace({'Macho': 'Masculino'})
df['rm_rec_cnrm_ds'] = df['rm_rec_cnrm_ds'].str.replace('Tenho', 'Possuo', regex=False)
df['curso_nome_limpo'] = df['curso_nome'].apply(limpar_nome_curso)
df['regiao_nascimento'] = df['rg_uf_ds'].map(REGIOES_BRASIL)
df['regiao_graduacao'] = df['estado_graduacao'].map(REGIOES_BRASIL)
df['regiao_crm'] = df['uf_crm_ds'].map(REGIOES_BRASIL)
df['regiao_vaga'] = df['vaga_uf'].map(REGIOES_BRASIL)

print("📊 Gerando agregações públicas...")
dados_publicos = {
    'dashboard': {},
    'mapas': {}
}

# --- DADOS PARA O DASHBOARD ---
# Contagens para gráficos de barras
bar_cols = ['raca_ds', 'sexo_ds', 'estado_civil_ds', 'ident_genero_ds',
            'orientacao_sexual_ds', 'tem_nome_social', 'aa_tipo_ds',
            'pais_formacao_ds', 'rm_rec_cnrm_ds', 'tit_esp_amb_ds',
            'rm_1_esp_medica_ds', 'rm_2_esp_medica_ds', 'amb_1_esp_medica_ds',
            'amb_2_esp_medica_ds', 'curso_nome_limpo', 'regiao_nascimento', 'regiao_vaga']
for col in bar_cols:
    dados_publicos['dashboard'][col] = df[col].value_counts().to_dict()

# Dados para histogramas (apenas a série de dados)
hist_cols = ['idade', 'tempo_graduado']
for col in hist_cols:
    # ===== CORREÇÃO APLICADA AQUI =====
    # Usamos .tolist() para converter os tipos de dados do NumPy para tipos nativos do Python
    dados_publicos['dashboard'][col] = df[col].dropna().tolist()

# Dados de apropriação
aprop_cols = ['apropriacao_redes', 'apropriacao_coordenacao', 'apropriacao_gestao', 'apropriacao_evidencias', 'experiencia_digital']
for col in aprop_cols:
    dados_publicos['dashboard'][col] = df[col].value_counts().to_dict()

# Dados de fluxo entre regiões
momentos = {'Nascimento': 'regiao_nascimento', 'Graduação': 'regiao_graduacao', 'CRM': 'regiao_crm', 'Vaga': 'regiao_vaga'}
dados_regioes = []
for momento, coluna in momentos.items():
    if coluna in df.columns:
        contagem = df[coluna].value_counts()
        for regiao, qtd in contagem.items():
            dados_regioes.append({'Momento': momento, 'Região': regiao, 'Quantidade': qtd})
dados_publicos['dashboard']['fluxo_regional'] = dados_regioes


# --- DADOS PARA OS MAPAS ---
map_cols = ['rg_uf_ds', 'estado_graduacao', 'uf_crm_ds', 'vaga_uf']
for col in map_cols:
    dados_publicos['mapas'][col] = df[col].value_counts().to_dict()

# Agregação de vagas por município
vagas_municipios = df.dropna(subset=['vaga_uf', 'vaga_municipio', 'curso_nome_limpo'])
vagas_agg = vagas_municipios.groupby(['vaga_uf', 'vaga_municipio'])['curso_nome_limpo'].apply(list).reset_index()
dados_publicos['mapas']['vagas_por_municipio'] = vagas_agg.to_dict(orient='records')


# --- SALVAR ARQUIVO PÚBLICO ---
with open('dados_publicos.json', 'w', encoding='utf-8') as f:
    json.dump(dados_publicos, f, ensure_ascii=False, indent=2)

print("✅ Arquivo 'dados_publicos.json' gerado com sucesso!")
print("   Você já pode executar 'python app_principal.py' e enviar seu projeto para o GitHub.")