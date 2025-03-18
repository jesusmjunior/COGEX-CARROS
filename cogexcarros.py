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

# ================== FUNÇÃO PARA EXPORTAR PDF VIA HTML ==================
def exportar_pdf_html(dataframe):
    html_content = f"""
    <html>
    <head><style>
    body {{ font-family: Arial; margin: 30px; }}
    h1 {{ text-align: center; }}
    footer {{ position: fixed; bottom: 0; text-align: center; width: 100%; font-size: 12px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 12px; }}
    </style></head>
    <body>
        <h1>COGEX CARROS - Corregedoria do Foro Extrajudicial</h1>
        <table>
            <tr>{''.join(f'<th>{col}</th>' for col in dataframe.columns)}</tr>
            {''.join(f'<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>' for row in dataframe.head(15).values)}
        </table>
        <footer>Endereço: Rua da Corregedoria, Nº 123, Cidade, Estado</footer>
    </body>
    </html>
    """
    st.sidebar.download_button(
        label="📄 Exportar PDF Trimestral",
        data=html_content,
        file_name="Relatorio_Trim_COGEX_CARROS.html",
        mime='text/html'
    )

# ================== LÓGICA POR ABA ==================
if aba_selecionada == 'VIAGEM':
    st.header("🛣️ Controle de Viagem Semanal")
    df['INICIO(DATA)'] = pd.to_datetime(df['INICIO(DATA)'], errors='coerce')
    df['FIM(DATA)'] = pd.to_datetime(df['FIM(DATA)'], errors='coerce')

    # Filtros de data
    st.sidebar.subheader("📅 Filtro de Data")
    data_inicio = st.sidebar.date_input("Data Início:", df['INICIO(DATA)'].min())
    data_fim = st.sidebar.date_input("Data Fim:", df['FIM(DATA)'].max())

    # Outros filtros
    motoristas = st.sidebar.multiselect("Nome do Motorista:", df['NOME DO MOTORISTA'].dropna().unique())
    tipo_veiculo = st.sidebar.multiselect("Tipo do Veículo:", df['TIPO DO VEÍCULO'].dropna().unique())
    viagem_ferias = st.sidebar.multiselect("Viagem/Férias:", df['VIAGEM/FÉRIAS'].dropna().unique())

    df_filtrado = df.copy()
    df_filtrado = df_filtrado[(df_filtrado['INICIO(DATA)'] >= pd.to_datetime(data_inicio)) & (df_filtrado['FIM(DATA)'] <= pd.to_datetime(data_fim))]

    if motoristas:
        df_filtrado = df_filtrado[df_filtrado['NOME DO MOTORISTA'].isin(motoristas)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado['TIPO DO VEÍCULO'].isin(tipo_veiculo)]
    if viagem_ferias:
        df_filtrado = df_filtrado[df_filtrado['VIAGEM/FÉRIAS'].isin(viagem_ferias)]

    df_filtrado['QUILOMETRAGEM SEMANAL'] = (df_filtrado['FIM(DATA)'].dt.day - df_filtrado['INICIO(DATA)'].dt.day).fillna(0)

    resumo_dados(df_filtrado)

    st.write("### 📄 Registros Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    bar_data = df_filtrado.groupby('NOME DO MOTORISTA')['QUILOMETRAGEM SEMANAL'].sum().reset_index()
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x=alt.X('NOME DO MOTORISTA:N', sort='-y'),
        y=alt.Y('QUILOMETRAGEM SEMANAL:Q'),
        tooltip=['NOME DO MOTORISTA', 'QUILOMETRAGEM SEMANAL']
    ).properties(title="Quilometragem por Motorista (Semanal)", height=400)
    st.altair_chart(bar_chart, use_container_width=True)

    if 'LINK DA FOTO' in df_filtrado.columns:
        df_filtrado['FOTO PAINEL'] = df_filtrado['LINK DA FOTO'].apply(lambda x: f"[Ver Foto]({x})" if pd.notnull(x) else '-')
        st.write(df_filtrado[['NOME DO MOTORISTA', 'TIPO DO VEÍCULO', 'INICIO(DATA)', 'FIM(DATA)', 'QUILOMETRAGEM SEMANAL', 'FOTO PAINEL']])

    botao_download(df_filtrado, "controle_viagem.csv")
    exportar_pdf_html(df_filtrado)

elif aba_selecionada == 'Dia a dia':
    st.header("📅 Controle Dia a Dia")

    st.sidebar.subheader("📅 Filtro de Data")
    df['DATA DO REGISTRO'] = pd.to_datetime(df['DATA DO REGISTRO'], errors='coerce')
    data_inicio = st.sidebar.date_input("Data Início:", df['DATA DO REGISTRO'].min())
    data_fim = st.sidebar.date_input("Data Fim:", df['DATA DO REGISTRO'].max())

    motoristas = st.sidebar.multiselect("Nome do Motorista:", df['NOME DO MOTORISTA'].dropna().unique())
    tipo_veiculo = st.sidebar.multiselect("Tipo do Veículo:", df['TIPO DO VEÍCULO'].dropna().unique())

    df_filtrado = df.copy()
    df_filtrado = df_filtrado[(df_filtrado['DATA DO REGISTRO'] >= pd.to_datetime(data_inicio)) & (df_filtrado['DATA DO REGISTRO'] <= pd.to_datetime(data_fim))]

    if motoristas:
        df_filtrado = df_filtrado[df_filtrado['NOME DO MOTORISTA'].isin(motoristas)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado['TIPO DO VEÍCULO'].isin(tipo_veiculo)]

    resumo_dados(df_filtrado)
    st.write("### 📄 Registros Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    if 'QUILOMETRAGEM' in df_filtrado.columns:
        bar_data = df_filtrado.groupby('NOME DO MOTORISTA')['QUILOMETRAGEM'].sum().reset_index()
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=alt.X('NOME DO MOTORISTA:N', sort='-y'),
            y=alt.Y('QUILOMETRAGEM:Q'),
            tooltip=['NOME DO MOTORISTA', 'QUILOMETRAGEM']
        ).properties(title="Quilometragem Total por Motorista", height=400)
        st.altair_chart(bar_chart, use_container_width=True)

    botao_download(df_filtrado, "controle_dia_a_dia.csv")
    exportar_pdf_html(df_filtrado)

else:
    st.header("📄 Sinistros")
    resumo_dados(df)
    st.dataframe(df, use_container_width=True)
    botao_download(df, "sinistros.csv")
    exportar_pdf_html(df)

# ================== MENSAGEM FINAL ==================
st.success("✅ Dashboard carregado com sucesso!")
