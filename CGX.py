import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from io import BytesIO

# ================== CONFIGURAÇÃO DO DASHBOARD ==================
st.set_page_config(
    page_title="📊 Dashboard Controle de Carros",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== INSERE ROBOZINHO DISCRETO ==================
st.markdown("""
    <style>
    .robozinho {
        position: fixed;
        bottom: 50px;
        right: 20px;
        z-index: 100;
        text-align: center;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0% { transform: translatey(0px); }
        50% { transform: translatey(-10px); }
        100% { transform: translatey(0px); }
    }
    </style>
    <div class="robozinho">
        <a href="https://www.appsheet.com/start/8169fb9c-03d6-4aad-9b6e-ce630d97d6e7" target="_blank">
            <img src="https://i.imgur.com/EYkDgBd.png" alt="Robozinho" style="width:70px;">
            <div style="font-size:10px; color:gray;">by CGX.JJ 2025</div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.title("🚗 Dashboard Controle Trimestral de Carros")
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# ================== FUNÇÃO PARA CARREGAR DADOS ==================
@st.cache_data(ttl=3600)
def carregar_dados():
    sheet_id = "1uKsmcO4AO2Q1VzzsYHIeAT_5QNrA7hFcX5zCWwgG_FI"
    base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="
    
    sheets_urls = {
        "Dia a dia": f"{base_url}Dia%20a%20dia",
        "VIAGEM": f"{base_url}VIAGEM",
        "Sinistro": f"{base_url}SINISTRO"
    }
    sheets = {}
    for sheet, url in sheets_urls.items():
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.upper()
        sheets[sheet] = df
    return sheets

sheets = carregar_dados()

# ================== SIDEBAR - SELEÇÃO DE ABA ==================
st.sidebar.header("📂 Selecione uma Aba")
tabs = list(sheets.keys())
aba_selecionada = st.sidebar.radio("Selecione uma aba:", tabs)
df = sheets[aba_selecionada]

st.sidebar.write("🔎 **Colunas carregadas:**")
st.sidebar.write(list(df.columns))

# ================== FILTROS NO TOPO ==================
st.subheader("🔽 Filtros")

if aba_selecionada == 'Dia a dia':
    df['DATA DO REGISTRO'] = pd.to_datetime(df['DATA DO REGISTRO'], errors='coerce')
    data_inicio = st.date_input("Data Início:", df['DATA DO REGISTRO'].min())
    data_fim = st.date_input("Data Fim:", df['DATA DO REGISTRO'].max())

    motoristas = st.multiselect("Nome do Motorista:", df['NOME DO MOTORISTA'].dropna().unique())
    tipo_veiculo = st.multiselect("Tipo do Veículo:", df['TIPO DO VEÍCULO'].dropna().unique())

    df_filtrado = df.copy()
    df_filtrado = df_filtrado[(df_filtrado['DATA DO REGISTRO'] >= pd.to_datetime(data_inicio)) & (df_filtrado['DATA DO REGISTRO'] <= pd.to_datetime(data_fim))]

    if motoristas:
        df_filtrado = df_filtrado[df_filtrado['NOME DO MOTORISTA'].isin(motoristas)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado['TIPO DO VEÍCULO'].isin(tipo_veiculo)]

    st.write("### 📄 Registros Filtrados")
    st.dataframe(df_filtrado.drop(columns=[col for col in df_filtrado.columns if 'UNNAMED' in col]), use_container_width=True)

    # ================== GRÁFICO QUILOMETRAGEM POR MOTORISTA ==================
    if 'QUILOMETRAGEM' in df_filtrado.columns:
        df_agrupado = df_filtrado.groupby('NOME DO MOTORISTA')['QUILOMETRAGEM'].sum().reset_index()
        bar_chart = alt.Chart(df_agrupado).mark_bar().encode(
            x=alt.X('NOME DO MOTORISTA:N', sort='-y'),
            y=alt.Y('QUILOMETRAGEM:Q'),
            tooltip=['NOME DO MOTORISTA', 'QUILOMETRAGEM']
        ).properties(title="Quilometragem Total por Motorista", height=400)
        st.altair_chart(bar_chart, use_container_width=True)

# ================== OUTRAS ABAS (EXEMPLO) ==================
else:
    st.write("### 📄 Registros")
    st.dataframe(df.drop(columns=[col for col in df.columns if 'UNNAMED' in col]), use_container_width=True)

# ================== RODAPÉ ==================
st.markdown("""
    <hr style='margin-top:50px;'>
    <div style='text-align:center; color:gray;'>© 2025 - COGEX CARROS - Corregedoria do Foro Extrajudicial</div>
""", unsafe_allow_html=True)
