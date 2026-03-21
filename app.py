import streamlit as st
import pandas as pd
import pydeck as pdk
import time

# --- 1. MOCK DATA (Simulando o Banco de Dados) ---
# Nossa farmácia (Destino)
FARMACIA_DESTINO = {'nome': 'Farmácia Alpha', 'lat': -23.5615, 'lon': -46.6533}

# Catálogo de produtos disponíveis na rede
PRODUTOS_DISPONIVEIS = ["Insulina NPH", "Reagente PCR", "Dipirona Lote X", "Luvas Nitrílicas"]

# Laboratórios e Distribuidoras (Origens)
dados_fornecedores = {
    'id': [1, 2, 3],
    'nome': ['Lab Central SP', 'Distribuidora Beta', 'FarmaLog Health'],
    'lat': [-23.5505, -23.5750, -23.5320],
    'lon': [-46.6333, -46.6800, -46.6120],
    'produtos': [
        ["Insulina NPH", "Dipirona Lote X"], 
        ["Reagente PCR", "Luvas Nitrílicas"], 
        ["Insulina NPH", "Reagente PCR", "Dipirona Lote X"]
    ],
    'refrigerado': [True, False, True] # Indica se possuem frota refrigerada
}
df_fornecedores = pd.DataFrame(dados_fornecedores)

# --- 2. CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="HealthLog B2B", layout="wide")
st.title("💊 HealthLog: Marketplace B2B (Modo Offline)")

# --- 3. INTERFACE DE PEDIDO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Novo Pedido")
    item_selecionado = st.selectbox("Selecione o Insumo/Medicamento", PRODUTOS_DISPONIVEIS)
    qtd = st.number_input("Quantidade (Caixas/Unidades)", min_value=1)
    
    # Filtra fornecedores que têm o produto selecionado
    fornecedores_validos = df_fornecedores[
        df_fornecedores['produtos'].apply(lambda x: item_selecionado in x)
    ]
    
    st.markdown("### Fornecedores Disponíveis")
    if not fornecedores_validos.empty:
        # Cria opções amigáveis para o Selectbox
        opcoes_fornecedores = fornecedores_validos['nome'].tolist()
        fornecedor_escolhido = st.selectbox("Escolha a origem", opcoes_fornecedores)
        
        # Pega os dados do fornecedor escolhido
        dados_escolhido = fornecedores_validos[fornecedores_validos['nome'] == fornecedor_escolhido].iloc[0]
        
        st.write(f"**Frota Refrigerada:** {'✅ Sim' if dados_escolhido['refrigerado'] else '❌ Não'}")
        
        if st.button("🚀 Solicitar Coleta", type="primary"):
            st.session_state['pedido_ativo'] = True
            st.session_state['origem_lat'] = dados_escolhido['lat']
            st.session_state['origem_lon'] = dados_escolhido['lon']
            st.session_state['nome_origem'] = dados_escolhido['nome']
    else:
        st.warning("Nenhum fornecedor possui este item no momento.")

# --- 4. O MAPA (ESTILO UBER) ---
with col2:
    st.header("2. Rastreamento e Logística")
    map_placeholder = st.empty()

    def render_map(current_lon, current_lat, show_driver=True):
        # Pontos fixos (Todos os fornecedores + Farmácia destino)
        places_layer = pdk.Layer(
            'ScatterplotLayer',
            data=df_fornecedores,
            get_position='[lon, lat]',
            get_color='[0, 100, 255, 160]', # Azul para fornecedores
            get_radius=200,
            pickable=True
        )
        
        destino_layer = pdk.Layer(
            'ScatterplotLayer',
            data=pd.DataFrame([FARMACIA_DESTINO]),
            get_position='[lon, lat]',
            get_color='[0, 200, 0, 180]', # Verde para sua farmácia
            get_radius=250,
        )

        layers = [places_layer, destino_layer]

        # Camada do motoboy/veículo
        if show_driver:
            driver_layer = pdk.Layer(
                'ScatterplotLayer',
                data=pd.DataFrame([{'lat': current_lat, 'lon': current_lon}]),
                get_position='[lon, lat]',
                get_color='[255, 50, 0, 200]', # Vermelho para o veículo
                get_radius=150,
            )
            layers.append(driver_layer)

        # Configuração da visão inicial do mapa
        view_state = pdk.ViewState(
            latitude=(current_lat + FARMACIA_DESTINO['lat']) / 2 if show_driver else FARMACIA_DESTINO['lat'],
            longitude=(current_lon + FARMACIA_DESTINO['lon']) / 2 if show_driver else FARMACIA_DESTINO['lon'],
            zoom=12,
            pitch=45,
        )

        return pdk.Deck(map_style='mapbox://styles/mapbox/dark-v10', initial_view_state=view_state, layers=layers, tooltip={"text": "{nome}"})

    # Lógica de exibição e animação
    if 'pedido_ativo' not in st.session_state:
        # Mapa estático mostrando a rede
        map_placeholder.pydeck_chart(render_map(FARMACIA_DESTINO['lon'], FARMACIA_DESTINO['lat'], show_driver=False))
        st.info("Aguardando novo pedido. O mapa mostra a rede de laboratórios cadastrados em azul e a sua farmácia em verde.")
    
    else:
        # Animação da entrega
        origem_lon = st.session_state['origem_lon']
        origem_lat = st.session_state['origem_lat']
        dest_lon = FARMACIA_DESTINO['lon']
        dest_lat = FARMACIA_DESTINO['lat']
        
        st.success(f"📦 Veículo a caminho saindo de **{st.session_state['nome_origem']}**!")
        
        passos = 30 # Quantidade de "quadros" da animação
        for i in range(passos + 1):
            # Interpolação linear da rota (linha reta para o MVP)
            lon_atual = origem_lon + (dest_lon - origem_lon) * (i / passos)
            lat_atual = origem_lat + (dest_lat - origem_lat) * (i / passos)
            
            map_placeholder.pydeck_chart(render_map(lon_atual, lat_atual, show_driver=True))
            time.sleep(0.15) # Velocidade da animação
            
        st.success("✅ Carga entregue e temperatura validada!")
        
        # Botão para resetar o estado e fazer um novo pedido
        if st.button("Fazer novo pedido"):
            del st.session_state['pedido_ativo']
            st.rerun()
