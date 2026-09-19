import streamlit as st

# CONFIGURACIÓN
def configurar_interface():
    st.set_page_config(page_title="Investoros Dashboard",layout="wide")
    st.markdown("""<style>
    .st-key-componentes button,.st-key-componentes button:hover,.st-key-componentes button:focus,
    .st-key-componentes button:active,.st-key-relacional button,.st-key-relacional button:hover,
    .st-key-relacional button:focus,.st-key-relacional button:active,.st-key-analisis button,
    .st-key-analisis button:hover,.st-key-analisis button:focus,.st-key-analisis button:active {
        background-color: #d2d2d2 !important;
        border-color: #333333 !important;
    }
    </style>
    """,unsafe_allow_html=True)
    st.markdown("""<style>
    section.stMain .block-container {padding-top: 2rem;}
    </style>""",unsafe_allow_html=True)

# SIDEBAR
def mostrar_sidebar(reset_dashboard):
    with st.sidebar:
        st.markdown("""
        <style>
        button[title="View fullscreen"] {
            display: none !important;
        }
        </style>
        """,unsafe_allow_html=True)
        st.image("multimedia/INVESTOROS_GRIS.png")
        # TICKER
        st.markdown("**TICKER**")
        ticker = st.text_input("Ticker",value="",placeholder="Enter ticker",
            label_visibility="collapsed",key="ticker",on_change=reset_dashboard)
        # PERIODO
        st.markdown("**PERIODO**")
        period = st.selectbox("Period",["Fiscal Year","Fiscal Quarter"],
            index=0,label_visibility="collapsed",key="period")
    return ticker,period

# HEADER
def mostrar_header(empresa,mercado,industria,sector):
    with st.container():
        st.markdown(f"# ANÁLISIS DE: {empresa.upper()}")
        st.markdown(f"**Sector:** {sector}")
        st.markdown(f"**Industria:** {industria}")

# CONTENIDO
def mostrar_contenido(financial_section,financial_relational_charts,financial_market_relational_charts,calificacion_financiera,data,x_column,datos_norm,valoraciones,valoraciones_norm,metricas_y,period,formato_calificacion):
    if st.session_state.section == "Crecimiento":
        financial_section(data,x_column,"Crecimiento",["Revenue","CapEx","FCF"],metricas_y,period)
    elif st.session_state.section == "Rentabilidad":
        financial_section(data,x_column,"Rentabilidad",["Operating Margin","ROIC","FCF margin"],metricas_y,period)
    elif st.session_state.section == "Solidez financiera":
        financial_section(data,x_column,"Solidez financiera",["Debt/EBITDA","Debt/Equity","Current ratio"],metricas_y,period)
    elif st.session_state.section == "Valoraciones":
        financial_section(valoraciones,x_column,"Valoraciones",["P/S","P/E","P/B","P/FCF"],metricas_y,period)
    elif st.session_state.section == "Financiero":
        financial_relational_charts(datos_norm)
    elif st.session_state.section == "Bursátil financiero":
        financial_market_relational_charts(datos_norm,valoraciones_norm)
    elif st.session_state.section == "Calificacion financiera":
        calificacion = calificacion_financiera(metricas_y)
        puntos = calificacion["Puntos"]

        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>Calificación financiera</h3>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("<h4 >Crecimiento</h4>", unsafe_allow_html=True)
                st.markdown(f"**Revenue:** {formato_calificacion(puntos['Revenue'])}", unsafe_allow_html=True)
                st.markdown(f"**FCF:** {formato_calificacion(puntos['FCF'])}", unsafe_allow_html=True)
                st.markdown("**CapEx:** No aplica")
                st.markdown(f"**Promedio:** {formato_calificacion(calificacion['Crecimiento'])}", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("<h4 >Rentabilidad</h4>", unsafe_allow_html=True)
                st.markdown(f"**Operating Margin:** {formato_calificacion(puntos['Operating Margin'])}", unsafe_allow_html=True)
                st.markdown(f"**ROIC:** {formato_calificacion(puntos['ROIC'])}", unsafe_allow_html=True)
                st.markdown(f"**FCF margin:** {formato_calificacion(puntos['FCF margin'])}", unsafe_allow_html=True)
                st.markdown(f"**Promedio:** {formato_calificacion(calificacion['Rentabilidad'])}", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("<h4 >Solidez financiera</h4>", unsafe_allow_html=True)
                st.markdown(f"**Debt/Equity:** {formato_calificacion(puntos['Debt/Equity'])}", unsafe_allow_html=True)
                st.markdown(f"**Debt/EBITDA:** {formato_calificacion(puntos['Debt/EBITDA'])}", unsafe_allow_html=True)
                st.markdown(f"**Current ratio:** {formato_calificacion(puntos['Current ratio'])}", unsafe_allow_html=True)
                st.markdown(f"**Promedio:** {formato_calificacion(calificacion['Solidez financiera'])}", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown(f"<h4 >Calificación total: {formato_calificacion(calificacion['Total'])}</h4>", unsafe_allow_html=True)
                st.markdown("**Métricas a mejorar:**")
                for metrica in calificacion["Métricas a mejorar"]:
                    st.markdown(f"- {metrica}")

# NAVEGACION
def navegacion():
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
            if st.button("CALIFICACIÓN FINANCIERA",use_container_width=True):
                st.session_state.section = "Calificacion financiera"
            if st.button("CALIFICACION BURSÁTIL",use_container_width=True):
                st.session_state.section = "Calificacion bursatil"
            if st.button("RANGOS DE PRECIO",use_container_width=True):
                st.session_state.section = "Analisis integral"