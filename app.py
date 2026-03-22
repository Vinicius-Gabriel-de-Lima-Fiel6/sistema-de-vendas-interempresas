import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

# Configura a página para ocupar a tela toda
st.set_page_config(layout="wide", page_title="Mapa de Vendas B2B")

# 1. Dados de Teste (50 pontos de venda)
df = pd.DataFrame({
    'lat': np.random.uniform(-23.60, -23.50, 50),
    'lon': np.random.uniform(-46.70, -46.60, 50),
    'valor': np.random.randint(5000, 100000, 50)
})

# 2. Controle Lateral (Sidebar)
st.sidebar.title("Controles do Mapa")
escala = st.sidebar.slider("Altura das Torres", 1, 200, 50)
cor = st.sidebar.color_picker("Cor das Torres", "#0072B2")

# Converter cor HEX para RGB para o Pydeck
def hex_to_rgb(h):
    h = h.lstrip('#')
    return list(int(h[i:i+2], 16) for i in (0, 2, 4)) + [200]

# 3. Definição da Camada 3D (Estilo Uber)
layer = pdk.Layer(
    "ColumnLayer",
    df,
    get_position=['lon', 'lat'],
    get_elevation='valor',
    elevation_scale=escala, # Controlado pelo slider
    radius=150,
    get_fill_color=hex_to_rgb(cor),
    pickable=True,
    extruded=True, # Garante o efeito 3D
)

# 4. Renderização do Mapa
view_state = pdk.ViewState(latitude=-23.55, longitude=-46.65, zoom=11, pitch=45)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='light',
    tooltip={"text": "Venda: R${valor}"}
))
