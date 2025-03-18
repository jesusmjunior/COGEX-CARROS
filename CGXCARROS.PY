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

st.title("🚗 Dashboard Controle Trimestral de Carros")
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# ================== INSERE ROBOZINHO DISCRETO ==================
st.markdown("""
    <div style="position: fixed; bottom: 50px; right: 20px; z-index:100; text-align:center;">
        <a href="https://www.appsheet.com/start/8169fb9c-03d6-4aad-9b6e-ce630d97d6e7" target="_blank">
            <img src="https://i.imgur.com/umR6L1P.png" alt="Robozinho" style="width:70px; animation: float 3s ease-in-out infinite;">
            <div style="font-size:10px; color:gray;">by CGX.JJ 2025</div>
        </a>
    </div>
    <style>
        @keyframes float { 0% { transform: translatey(0px); } 50% { transform: translatey(-10px); } 100% { transform: translatey(0px); } }
    </style>
""", unsafe_allow_html=True)

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

# (restante do código permanece igual)
