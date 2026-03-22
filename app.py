import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="SaaS B2B Map")

# 1. Dados de Teste (Empresas e Vendas)
data = pd.DataFrame({
    'lat': np.random.uniform(-23.58, -23.52, 50),
    'lon': np.random.uniform(-46.68, -46.62, 50),
    'nome': [f"Empresa {i}" for i in range(50)],
    'vendas': np.random.randint(5000, 100000, 50) # Valor que define a altura
})

# 2. Barra Lateral de Controle
st.sidebar.header("Painel de Controle")
altura_multiplicador = st.sidebar.slider("Aumentar Altura das Torres", 1, 100, 20)
filtro_valor = st.sidebar.number_input("Ver vendas acima de (R$):", 0, 100000, 10000)

df_filtrado = data[data['vendas'] >= filtro_valor]

# 3. Camada de Colunas (Onde o controle acontece)
layer = pdk.Layer(
    "ColumnLayer",
    df_filtrado,
    get_position=['lon', 'lat'],
    get_elevation='vendas',      # A altura vem da coluna 'vendas'
    elevation_scale=altura_multiplicador, # O slider controla isso!
    radius=100,                  # Largura da torre
    get_fill_color=[18, 115, 222, 200], # Azul Uber
    pickable=True,
    extruded=True,               # Ativa o 3D
)

# 4. Configuração da Câmera (Inclinada para ver o 3D)
view_state = pdk.ViewState(
    latitude=-23.55,
    longitude=-46.65,
    zoom=12,
    pitch=45, # Inclinação da câmera
    bearing=30
)

# 5. Exibição
st.title("Controle de Vendas por Região")
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='light',
    tooltip={"text": "{nome}\nTotal: R${vendas}"}
))

st.write(f"Empresas exibidas: {len(df_filtrado)}")
