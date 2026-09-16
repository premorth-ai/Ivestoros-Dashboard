import streamlit as st
from S04_graficos import financial_metric_charts,financial_valuation_charts,financial_relational_charts,financial_market_relational_charts

# SECCIONES FINANCIERAS INDIVIDUALES
def financial_section(data,x_column,title,metrics):
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>",unsafe_allow_html=True)
    if title == "Valoraciones":
        financial_valuation_charts(data,x_column,metrics)
    else:
        financial_metric_charts(data,x_column,metrics)

# SECCIONES FINANCIERAS RELACIONADAS
def financial_relational_section(datos_norm):
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Relaciones financieras (datos normalizados)</h3>",unsafe_allow_html=True)
    financial_relational_charts(datos_norm)

def financial_market_relational_section(datos_norm,valoraciones_norm):
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Relaciones Bursátiles (Datos normalizados)</h3>",unsafe_allow_html=True)
    financial_market_relational_charts(datos_norm,valoraciones_norm)

# SELECCIÓN DE DATOS
def get_company_data(metricas_y,metricas_q,valoraciones_y,valoraciones_q,period):
    if period == "Fiscal Year":
        return metricas_y.copy(),valoraciones_y.copy(),"Fiscal Year"
    return metricas_q.copy(),valoraciones_q.copy(),"Fiscal Quarter"

# ESTADO DE LA APLICACIÓN
def inicializar_estado():
    if "section" not in st.session_state:
        st.session_state.section = None
    if "loaded_ticker" not in st.session_state:
        st.session_state.loaded_ticker = None
    if "metricas_y" not in st.session_state:
        st.session_state.metricas_y = None
    if "metricas_q" not in st.session_state:
        st.session_state.metricas_q = None
    if "valoraciones_y" not in st.session_state:
        st.session_state.valoraciones_y = None
    if "valoraciones_q" not in st.session_state:
        st.session_state.valoraciones_q = None
    if "valoraciones_norm" not in st.session_state:
        st.session_state.valoraciones_norm = None
    if "mercado_y" not in st.session_state:
        st.session_state.mercado_y = None
    if "mercado_q" not in st.session_state:
        st.session_state.mercado_q = None

# RESETEAR
def reset_dashboard():
    st.session_state.section = None

# VALIDACIÓN DEL TICKER
def validar_ticker(ticker):
    if ticker == "":
        return None
    return ticker

# NORMALIZAR DATOS BASE 100
def normalizar_datos(datos_y,valoraciones_y):
    datos_norm = datos_y.copy()
    valoraciones_norm = valoraciones_y.copy()
    datos_norm["Debt/EBITDA Inverso"] = 1 / datos_norm["Debt/EBITDA"]
    for columna in datos_norm.columns[1:]:
        datos_norm[columna] = datos_norm[columna] / datos_norm[columna].iloc[0] * 100
    for columna in valoraciones_norm.columns[1:]:
        valoraciones_norm[columna] = valoraciones_norm[columna] / valoraciones_norm[columna].iloc[0] * 100
    return datos_norm,valoraciones_norm