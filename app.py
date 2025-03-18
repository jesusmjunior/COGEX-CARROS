import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# ================== CONFIGURAÇÃO DO DASHBOARD ==================
st.set_page_config(
    page_title="📊 Dashboard Controle de Carros",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        df.columns = df.columns.str.strip().str.upper()  # Normalização das colunas
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

# ================== FUNÇÃO AUXILIAR ==================
def botao_download(dataframe, filename):
    csv = dataframe.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label="⬇️ Baixar CSV Filtrado",
        data=csv.encode('utf-8-sig'),
        file_name=filename,
        mime='text/csv'
    )

def resumo_dados(dataframe):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de registros", dataframe.shape[0])
    with col2:
        st.metric("Colunas disponíveis", dataframe.shape[1])
    with col3:
        st.metric("Última atualização", datetime.now().strftime("%d/%m/%Y"))

# ================== LÓGICA POR ABA ==================
if aba_selecionada == 'VIAGEM':
    st.header("🛣️ Controle de Viagem Semanal")
    df['INICIO(DATA)'] = pd.to_datetime(df['INICIO(DATA)'], errors='coerce')
    df['FIM(DATA)'] = pd.to_datetime(df['FIM(DATA)'], errors='coerce')

    # Filtros
    motoristas = st.sidebar.multiselect("Nome do Motorista:", df['NOME DO MOTORISTA'].dropna().unique())
    tipo_veiculo = st.sidebar.multiselect("Tipo do Veículo:", df['TIPO DO VEÍCULO'].dropna().unique())
    viagem_ferias = st.sidebar.multiselect("Viagem/Férias:", df['VIAGEM/FÉRIAS'].dropna().unique())

    df_filtrado = df.copy()
    if motoristas:
        df_filtrado = df_filtrado[df_filtrado['NOME DO MOTORISTA'].isin(motoristas)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado['TIPO DO VEÍCULO'].isin(tipo_veiculo)]
    if viagem_ferias:
        df_filtrado = df_filtrado[df_filtrado['VIAGEM/FÉRIAS'].isin(viagem_ferias)]

    # Quilometragem semanal (FIM - INICIO)
    df_filtrado['QUILOMETRAGEM SEMANAL'] = (df_filtrado['FIM(DATA)'].dt.day - df_filtrado['INICIO(DATA)'].dt.day).fillna(0)

    resumo_dados(df_filtrado)

    st.write("### 📄 Registros Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    # Gráfico de barras - Quilometragem Semanal
    bar_data = df_filtrado.groupby('NOME DO MOTORISTA')['QUILOMETRAGEM SEMANAL'].sum().reset_index()
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x=alt.X('NOME DO MOTORISTA:N', sort='-y'),
        y=alt.Y('QUILOMETRAGEM SEMANAL:Q'),
        tooltip=['NOME DO MOTORISTA', 'QUILOMETRAGEM SEMANAL']
    ).properties(title="Quilometragem por Motorista (Semanal)", height=400)
    st.altair_chart(bar_chart, use_container_width=True)

    # Tabela com links para fotos
    st.write("### 📸 Fotos do Painel do Carro")
    if 'LINK DA FOTO' in df_filtrado.columns:
        df_filtrado['FOTO PAINEL'] = df_filtrado['LINK DA FOTO'].apply(lambda x: f"[Ver Foto]({x})" if pd.notnull(x) else '-')
        st.write(df_filtrado[['NOME DO MOTORISTA', 'TIPO DO VEÍCULO', 'INICIO(DATA)', 'FIM(DATA)', 'QUILOMETRAGEM SEMANAL', 'FOTO PAINEL']])

    botao_download(df_filtrado, "controle_viagem.csv")

elif aba_selecionada == 'Dia a dia':
    st.header("📅 Controle Dia a Dia")

    motoristas = st.sidebar.multiselect("Nome do Motorista:", df['NOME DO MOTORISTA'].dropna().unique())
    tipo_veiculo = st.sidebar.multiselect("Tipo do Veículo:", df['TIPO DO VEÍCULO'].dropna().unique())
    df_filtrado = df.copy()

    if motoristas:
        df_filtrado = df_filtrado[df_filtrado['NOME DO MOTORISTA'].isin(motoristas)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado['TIPO DO VEÍCULO'].isin(tipo_veiculo)]

    resumo_dados(df_filtrado)
    st.write("### 📄 Registros Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    # Gráfico de quilometragem
    if 'QUILOMETRAGEM' in df_filtrado.columns:
        bar_data = df_filtrado.groupby('NOME DO MOTORISTA')['QUILOMETRAGEM'].sum().reset_index()
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=alt.X('NOME DO MOTORISTA:N', sort='-y'),
            y=alt.Y('QUILOMETRAGEM:Q'),
            tooltip=['NOME DO MOTORISTA', 'QUILOMETRAGEM']
        ).properties(title="Quilometragem Total por Motorista", height=400)
        st.altair_chart(bar_chart, use_container_width=True)

    botao_download(df_filtrado, "controle_dia_a_dia.csv")

else:
    st.header("📄 Sinistros")
    resumo_dados(df)
    st.dataframe(df, use_container_width=True)
    botao_download(df, "sinistros.csv")

# ================== MENSAGEM FINAL ==================
st.success("✅ Dashboard carregado com sucesso!")
