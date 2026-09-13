import streamlit as st
from S02_datos import industrias

# CONFIGURACIÓN
def configurar_interface():
    st.set_page_config(page_title="Investoros Dashboard",layout="wide")
    st.markdown("""<style>
    .st-key-componentes button,
    .st-key-componentes button:hover,
    .st-key-componentes button:focus,
    .st-key-componentes button:active,
    .st-key-relacional button,
    .st-key-relacional button:hover,
    .st-key-relacional button:focus,
    .st-key-relacional button:active,
    .st-key-analisis button,
    .st-key-analisis button:hover,
    .st-key-analisis button:focus,
    .st-key-analisis button:active {
        background-color: #d2d2d2 !important;
        border-color: #333333 !important;
    }
    </style>
    """,unsafe_allow_html=True)
    st.markdown("""<style>
    section.stMain .block-container {padding-top: 2rem;}
    </style>""",unsafe_allow_html=True)

# SIDEBAR
def mostrar_interface(reset_dashboard):
    with st.sidebar:
        st.logo("multimedia/logo_premorth2.png")
        st.image("multimedia/INVESTOROS2.png")
        # TICKER
        st.markdown("**TICKER**")
        ticker = st.text_input("Ticker",value="",placeholder="Enter ticker",
            label_visibility="collapsed",key="ticker",on_change=reset_dashboard)
        # INDUSTRIA
        st.markdown("**INDUSTRIA**")
        industria = st.selectbox("Industry",industrias["industria"],index=None,
            placeholder="Select industry",label_visibility="collapsed",key="industria")
        # PERIODO
        st.markdown("**PERIODO**")
        period = st.selectbox("Period",["Fiscal Year","Fiscal Quarter"],
            index=0,label_visibility="collapsed",key="period")
    return ticker,period

# HEADER
def mostrar_header(empresa,precio_actual,marketcap_actual):
    with st.container():
        marketcap_actual = marketcap_actual/1000
        st.markdown(f"# ANÁLISIS DE: {empresa.upper()}")
        st.markdown(f"**Precio último cierre:** ${precio_actual}")
        st.markdown(f"**Market Cap último cierre:** {marketcap_actual:,.2f} B")


# CONTENIDO
def mostrar_contenido(financial_section,financial_relational_section,financial_market_relational_section,data,x_column,datos_norm):
    if st.session_state.section == "Crecimiento":
        financial_section(data,x_column,"Crecimiento",["revenue","capex","fcf"])
    elif st.session_state.section == "Rentabilidad":
        financial_section(data,x_column,"Rentabilidad",["operating_margin","roic","fcf_margin"],["operating_margin","roic","fcf_margin"])
    elif st.session_state.section == "Solidez financiera":
        financial_section(data,x_column,"Solidez financiera",["debt_ebitda","debt_equity","current_ratio"])
    elif st.session_state.section == "Valoraciones":
        financial_section(data,x_column,"Valoraciones",["ps","pe","pb","p_fcf"])
    elif st.session_state.section == "Financiero":
        financial_relational_section(datos_norm)
    elif st.session_state.section == "Bursátil financiero":
        financial_market_relational_section(datos_norm)

# NAVEGACION
def navigation():
    col1,col2,col3 = st.columns([1,1,1])
    with col1:
        with st.popover("📚 COMPONENTES FINANCIEROS",use_container_width=True,key="componentes"):
            if st.button("CRECIMIENTO",use_container_width=True):
                st.session_state.section = "Crecimiento"
            if st.button("RENTABILIDAD",use_container_width=True):
                st.session_state.section = "Rentabilidad"
            if st.button("SOLIDEZ FINANCIERA",use_container_width=True):
                st.session_state.section = "Solidez financiera"
            if st.button("RELACIONES FINANCIERAS",use_container_width=True):
                st.session_state.section = "Financiero"
    with col2:
        with st.popover("📊 COMPONENTES BURSATILES",use_container_width=True,key="relacional"):
            if st.button("VALORACIONES ",use_container_width=True):
                st.session_state.section = "Valoraciones"
            if st.button("RELACIONES BURSATILES",use_container_width=True):
                st.session_state.section = "Bursátil financiero"
    with col3:
        with st.popover("📋 ANÁLISIS",use_container_width=True,key="analisis"):
            if st.button("CALIFICACIÓN CONTABLE",use_container_width=True):
                st.session_state.section = "Analisis contable"
            if st.button("CALIFICACIÓN DE VALORACIONES",use_container_width=True):
                st.session_state.section = "Analisis valoraciones"
            if st.button("RANGO DE PRECIO",use_container_width=True):
                st.session_state.section = "Analisis integral"