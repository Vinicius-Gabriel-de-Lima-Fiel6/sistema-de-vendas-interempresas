import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

# Configuração da página SaaS
st.set_page_config(page_title="SaaS B2B - Painel de Logística", layout="wide")

st.title("Enterprise Sales Tracker - Uber Maps Control")
st.sidebar.header("Filtros de Vendas B2B")

# 1. Simulação de Dados de Vendas (Substitua pelo seu Banco de Dados/CSV depois)
@st.cache_data
def carregar_dados():
    # Criando 100 pontos de vendas aleatórios em São Paulo
    data = pd.DataFrame({
        'latitude': np.random.uniform(-23.60, -23.50, 100),
        'longitude': np.random.uniform(-46.70, -46.60, 100),
        'valor_venda': np.random.randint(1000, 50000, 100),
        'setor': np.random.choice(['Varejo', 'Indústria', 'Serviços'], 100)
    })
    return data

df = carregar_dados()

# 2. Controles na Barra Lateral (Sidebar)
setor_selecionado = st.sidebar.multiselect(
    "Filtrar por Setor Econômico",
    options=df['setor'].unique(),
    default=df['setor'].unique()
)

valor_minimo = st.sidebar.slider("Valor Mínimo da Transação (R$)", 0, 50000, 5000)

# 3. Filtragem Lógica
df_filtrado = df[
    (df['setor'].isin(setor_selecionado)) & 
    (df['valor_venda'] >= valor_minimo)
]

# 4. Configuração do Mapa Uber (Pydeck)
view_state = pdk.ViewState(
    latitude=-23.55,
    longitude=-46.65,
    zoom=11,
    pitch=50
)

# Camada de Hexágonos (estilo Uber) para ver densidade de vendas
layer = pdk.Layer(
    "HexagonLayer",
    df_filtrado,
    get_position=['longitude', 'latitude'],
    radius=200,
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
)

# 5. Renderização no Streamlit
st.write(f"Exibindo **{len(df_filtrado)}** transações filtradas.")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9', # Se ficar branco, mude para None ou 'light'
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "Setor: {setor}\nValor: R${valor_venda}"}
))

# Tabela de dados abaixo do mapa
if st.checkbox("Mostrar tabela de dados bruta"):
    st.dataframe(df_filtrado)
