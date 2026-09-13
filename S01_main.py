import streamlit as st

from S02_datos import consultar_web,no_sql_renombrar,cambiar_tipo
from S03_interface import (mostrar_interface,configurar_interface,mostrar_header,mostrar_contenido,navigation)
from S05_funciones import (
    financial_section,financial_relational_section,financial_market_relational_section,
    get_company_data,inicializar_estado,reset_dashboard,validar_ticker,normalizar_datos)
from S04_graficos import price_chart


# CONFIGURACIÓN
configurar_interface()

# ESTADO DE LA APLICACIÓN
inicializar_estado()

# SIDEBAR
ticker,period = mostrar_interface(reset_dashboard)

# VALIDACIÓN DEL TICKER
ticker = validar_ticker(ticker)
if ticker is None:
    if st.session_state.ticker == "":
        st.warning("Ingrese un ticker para comenzar.")
    else:
        st.error("Ticker no encontrado.")
else:
    if st.session_state.loaded_ticker != ticker:
        resultado = consultar_web(ticker)
        if resultado is None:
            st.error("Ticker no encontrado")
            ticker = None
        else:
            nombre,datos_y,datos_q,precio_actual,marketcap_actual = resultado
            datos_y,datos_q,precio_actual,marketcap_actual = no_sql_renombrar(datos_y,datos_q,precio_actual,marketcap_actual)
            datos_y,datos_q,precio_actual,marketcap_actual = cambiar_tipo(datos_y,datos_q,precio_actual,marketcap_actual)
            datos_norm = normalizar_datos(datos_y)
            st.session_state.loaded_ticker = ticker
            st.session_state.nombre = nombre
            st.session_state.datos_y = datos_y
            st.session_state.datos_q = datos_q
            st.session_state.datos_norm = datos_norm
            st.session_state.precio_actual = precio_actual
            st.session_state.marketcap_actual = marketcap_actual
    else:
        nombre = st.session_state.nombre
        datos_y = st.session_state.datos_y
        datos_q = st.session_state.datos_q
        datos_norm = st.session_state.datos_norm
        precio_actual = st.session_state.precio_actual
        marketcap_actual = st.session_state.marketcap_actual

    if ticker:
        empresa = nombre
        # SELECCIÓN DE DATOS
        data,x_column = get_company_data(datos_y,datos_q,period)

# HEADER
if ticker:
    mostrar_header(empresa,precio_actual,marketcap_actual)
    price_chart(data,x_column,precio_actual)

# NAVEGACIÓN
navigation()

# CONTENIDO
if ticker:
    mostrar_contenido(financial_section,financial_relational_section,
    financial_market_relational_section,data,x_column,datos_norm)