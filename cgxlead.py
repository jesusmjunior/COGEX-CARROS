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
tabs = list(sheets.keys()) + ["Ranking Motoristas"]
aba_selecionada = st.sidebar.radio("Selecione uma aba:", tabs)

# ================== FILTROS E LÓGICA PRINCIPAL ==================
if aba_selecionada == 'Dia a dia':
    df = sheets['Dia a dia']
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

    # ======== QUILOMETRAGEM REAL: ÚLTIMA - PRIMEIRA ========
    if 'QUILOMETRAGEM' in df_filtrado.columns:
        df_quilometragem = df_filtrado.sort_values('DATA DO REGISTRO').groupby('NOME DO MOTORISTA')['QUILOMETRAGEM'].agg(['first', 'last']).reset_index()
        df_quilometragem['KM_RODADOS'] = df_quilometragem['last'] - df_quilometragem['first']

        bar_chart = alt.Chart(df_quilometragem).mark_bar().encode(
            x=alt.X('NOME DO MOTORISTA:N', sort='-y'),
            y=alt.Y('KM_RODADOS:Q'),
            tooltip=['NOME DO MOTORISTA', 'KM_RODADOS']
        ).properties(title="Quilometragem Real por Motorista", height=400)
        st.altair_chart(bar_chart, use_container_width=True)

elif aba_selecionada == 'Ranking Motoristas':
    st.header("🏆 Ranking dos Motoristas")

    # ============ QUILOMETRAGEM RANK ============
    dia_df = sheets['Dia a dia']
    dia_df['DATA DO REGISTRO'] = pd.to_datetime(dia_df['DATA DO REGISTRO'], errors='coerce')
    df_quilometragem = dia_df.sort_values('DATA DO REGISTRO').groupby('NOME DO MOTORISTA')['QUILOMETRAGEM'].agg(['first', 'last']).reset_index()
    df_quilometragem['KM_RODADOS'] = df_quilometragem['last'] - df_quilometragem['first']

    top_km = df_quilometragem.sort_values(by='KM_RODADOS', ascending=False).head(5)

    st.subheader("🚗 Top 5 Quem Mais Rodou")
    st.dataframe(top_km[['NOME DO MOTORISTA', 'KM_RODADOS']])

    # ============ LAVAGEM RANK ============
    df_lavagem = dia_df[dia_df['OBS'].str.contains('lavagem', case=False, na=False)].groupby('NOME DO MOTORISTA').size().reset_index(name='TOTAL_LAVAGENS')
    top_lavagem = df_lavagem.sort_values(by='TOTAL_LAVAGENS', ascending=False).head(5)

    st.subheader("🧽 Top 5 Quem Mais Lavou")
    st.dataframe(top_lavagem)

    # ============ VIAGEM RANK ============
    viagem_df = sheets['VIAGEM']
    df_viagem = viagem_df.groupby('NOME DO MOTORISTA').size().reset_index(name='TOTAL_VIAGENS')
    top_viagem = df_viagem.sort_values(by='TOTAL_VIAGENS', ascending=False).head(5)

    st.subheader("✈️ Top 5 Quem Mais Viajou")
    st.dataframe(top_viagem)

    st.markdown("""
        <hr>
        <div style='text-align:center;'>
            🚗💨🥇 Parabéns aos motoristas destaque!<br>
            Cada motorista representado por um carrinho e bonequinho CGX!<br>
        </div>
    """, unsafe_allow_html=True)

else:
    df = sheets[aba_selecionada]
    st.write("### 📄 Registros")
    st.dataframe(df.drop(columns=[col for col in df.columns if 'UNNAMED' in col]), use_container_width=True)

# ================== RODAPÉ ==================
st.markdown("""
    <hr style='margin-top:50px;'>
    <div style='text-align:center; color:gray;'>© 2025 - COGEX CARROS - Corregedoria do Foro Extrajudicial</div>
""", unsafe_allow_html=True)
