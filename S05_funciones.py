import streamlit as st
from S04_graficos import financial_charts,financial_relational_charts,financial_market_relational_charts

# SECCIONES FINANCIERAS INDIVIDUALES
def financial_section(data,x_column,title,metrics):
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>",unsafe_allow_html=True)
    financial_charts(data,x_column,metrics)

# SECCIONES FINANCIERAS RELACIONADAS
def financial_relational_section(datos_norm):
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Relaciones financieras (datos normalizados)</h3>",unsafe_allow_html=True)
    financial_relational_charts(datos_norm)

# SECCIONES BURSATILES RELACIONADAS
def financial_market_relational_section(datos_norm):
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Relaciones Bursátiles (Datos normalizados)</h3>",unsafe_allow_html=True)
    financial_market_relational_charts(datos_norm)

# SELECCIÓN DE DATOS
def get_company_data(datos_y,datos_q,period):
    if period == "Fiscal Year":
        return datos_y.copy(),"fiscal_year"
    return datos_q.copy(),"fiscal_quarter"

# ESTADO DE LA APLICACIÓN
def inicializar_estado():
    if "section" not in st.session_state:
        st.session_state.section = None
    if "loaded_ticker" not in st.session_state:
        st.session_state.loaded_ticker = None
    if "datos_y" not in st.session_state:
        st.session_state.datos_y = None
    if "datos_q" not in st.session_state:
        st.session_state.datos_q = None

# RESETEAR
def reset_dashboard():
    st.session_state.section = None

# VALIDACIÓN DEL TICKER
def validar_ticker(ticker):
    if ticker == "":
        return None
    return ticker

# NORMALIZAR DATOS BASE 100
def normalizar_datos(datos_y):
    datos_norm = datos_y.copy()
    datos_norm["ebitda_deuda"] = 1 / datos_norm["debt_ebitda"]
    for columna in datos_norm.columns[1:]:
        datos_norm[columna] = datos_norm[columna] / datos_norm[columna].iloc[0] * 100
    return datos_norm