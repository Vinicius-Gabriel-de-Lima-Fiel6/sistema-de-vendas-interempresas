import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="SaaS B2B Intelligence")

# 1. GERADOR DE DADOS (Simulando Clientes Reais)
@st.cache_data
def carregar_dados():
    n = 80
    data = pd.DataFrame({
        'id': range(n),
        'empresa': [f"Cliente Corporativo {i}" for i in range(n)],
        'lat': np.random.uniform(-23.65, -23.45, n),
        'lon': np.random.uniform(-46.75, -46.55, n),
        'vendas': np.random.randint(5000, 150000, n),
        'saude_conta': np.random.choice(['Saudável', 'Em Risco', 'Crítico'], n)
    })
    # Lógica de cores baseada na saúde da conta
    color_map = {
        'Saudável': [0, 200, 100, 200],  # Verde
        'Em Risco': [255, 200, 0, 200],  # Amarelo
        'Crítico': [255, 0, 0, 200]      # Vermelho
    }
    data['cor'] = data['saude_conta'].map(color_map)
    return data

df = carregar_dados()

# 2. BARRA LATERAL (FUNCIONALIDADES)
st.sidebar.title("🏢 Gestão de Contas")

# Funcionalidade A: Busca Direta
busca_cliente = st.sidebar.selectbox("Localizar Cliente no Mapa", ["Todos"] + list(df['empresa']))

# Funcionalidade B: Filtro de Performance
min_vendas = st.sidebar.slider("Valor Mínimo em Carteira (R$)", 0, 150000, 5000)

# 3. LÓGICA DE FILTRAGEM
df_filtrado = df[df['vendas'] >= min_vendas]
if busca_cliente != "Todos":
    df_filtrado = df_filtrado[df_filtrado['empresa'] == busca_cliente]
    # Centraliza o mapa no cliente buscado
    lat_foco = df_filtrado['lat'].iloc[0]
    lon_foco = df_filtrado['lon'].iloc[0]
    zoom_foco = 15
else:
    lat_foco, lon_foco, zoom_foco = -23.55, -46.65, 11

# 4. DASHBOARD HEADER (MÉTRICAS)
col1, col2, col3 = st.columns(3)
col1.metric("Faturamento em Tela", f"R$ {df_filtrado['vendas'].sum():,.2f}")
col2.metric("Clientes Ativos", len(df_filtrado))
col3.metric("Ticket Médio", f"R$ {df_filtrado['vendas'].mean():,.2f}")

# 5. CONFIGURAÇÃO DA CAMADA 3D (UBER DECK.GL)
layer = pdk.Layer(
    "ColumnLayer",
    df_filtrado,
    get_position=['lon', 'lat'],
    get_elevation='vendas',
    elevation_scale=0.1, # Ajustado para escala de Reais
    radius=200,
    get_fill_color='cor', # Cor dinâmica vinda do DataFrame
    pickable=True,
    extruded=True,
)

# 6. RENDERIZAÇÃO
view_state = pdk.ViewState(latitude=lat_foco, longitude=lon_foco, zoom=zoom_foco, pitch=45)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/dark-v10', # Estilo escuro para destacar as cores
    tooltip={
        "html": "<b>Empresa:</b> {empresa}<br/><b>Vendas:</b> R${vendas}<br/><b>Status:</b> {saude_conta}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
))

# 7. TABELA DE EXPORTAÇÃO
with st.expander("Ver lista detalhada de empresas"):
    st.dataframe(df_filtrado[['empresa', 'vendas', 'saude_conta']])
