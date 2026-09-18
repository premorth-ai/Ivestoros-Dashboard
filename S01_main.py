import streamlit as st
from S02_datos import consultar_web
from S03_interface import (mostrar_interface,configurar_interface,mostrar_header,mostrar_contenido,navigation)
from S04_graficos import price_chart,financial_relational_charts,financial_market_relational_charts
from S05_funciones import (financial_section,get_company_data,inicializar_estado,
                           reset_dashboard,validar_ticker,normalizar_datos,determinar_tendencia,mostrar_evaluacion,calificacion_financiera)


# CONFIGURACIÓN
configurar_interface()

# ESTADO DE LA APLICACIÓN
inicializar_estado()

# PANTALLA DE CARGA INICIAL
pantalla_inicial = None
if "carga_inicial" not in st.session_state:
    st.session_state.carga_inicial = True
if st.session_state.carga_inicial:
    pantalla_inicial = st.empty()
    pantalla_inicial.markdown("""
    <style>
    .pantalla-inicial {position: fixed;top: 0;left: 0;width: 100vw;height: 100vh;background-color: white;
    z-index: 999998;display: flex;flex-direction: column;justify-content: center;align-items: center;}
    .pantalla-inicial h2 {margin: 0;font-size: 28px;}
    .pantalla-inicial p {margin-top: 12px;font-size: 18px;}
    .loader-inicial {width: 55px;height: 55px;border: 6px solid #e5e5e5;border-top: 6px solid #2C3490;
    border-radius: 50%;animation: girar 1s linear infinite;margin-top: 25px;}
    @keyframes girar {100% { transform: rotate(360deg); }}
    </style>
    <div class="pantalla-inicial" id="pantalla-inicial">
        <h2>Preparando INVESTOROS</h2>
        <p>Cargando dashboard...</p>
        <div class="loader-inicial"></div>
    </div>
    <script>
    window.addEventListener("load",function() {
        const pantalla = document.getElementById("pantalla-inicial");
        if (pantalla) {
            pantalla.style.display = "none";
        }
    });
    </script>
    """,unsafe_allow_html=True)

# SIDEBAR
ticker,period = mostrar_interface(reset_dashboard)

# VALIDACIÓN DEL TICKER
ticker = validar_ticker(ticker)
pantalla_carga = None
if ticker is None:
    if st.session_state.ticker == "":
        st.warning("Ingrese un ticker para comenzar.")
    else:
        st.error("Ticker no encontrado.")
else:
    if st.session_state.loaded_ticker != ticker or st.session_state.valoraciones_norm is None:
        pantalla_carga = st.empty()
        pantalla_carga.markdown(f"""
        <style>
        .pantalla-carga {{position: fixed;top: 0;left: 0;width: 100vw;height: 100vh;background-color: white;
        z-index: 999999;display: flex;flex-direction: column;justify-content: center;align-items: center;}}
        .pantalla-carga img {{width: 180px;margin-bottom: 25px;}}
        .pantalla-carga h2 {{margin: 0;font-size: 28px;}}
        .pantalla-carga p {{margin-top: 12px;font-size: 18px;}}
        .loader {{width: 55px;height: 55px;border: 6px solid #e5e5e5;border-top: 6px solid #2C3490;
        border-radius: 50%;animation: girar 1s linear infinite;margin-top: 25px;}}
        @keyframes girar {{100% {{ transform: rotate(360deg); }}}}
        </style>
        <div class="pantalla-carga">
            <h2>Analizando {ticker.upper()}</h2>
            <p>Obteniendo información financiera...</p>
            <div class="loader"></div>
        </div>
        """,unsafe_allow_html=True)
        
        resultado = consultar_web(ticker)
        
        if resultado is None:
            pantalla_carga.empty()
            st.error("Ticker no encontrado")
            ticker = None
        else:
            nombre,metricas_y,metricas_q,valoraciones_y,valoraciones_q,mercado_y,mercado_q,industrias_v = resultado
            datos_norm,valoraciones_norm = normalizar_datos(metricas_y,valoraciones_y)
            st.session_state.loaded_ticker = ticker
            st.session_state.nombre = nombre
            st.session_state.metricas_y = metricas_y
            st.session_state.metricas_q = metricas_q
            st.session_state.valoraciones_y = valoraciones_y
            st.session_state.valoraciones_q = valoraciones_q
            st.session_state.datos_norm = datos_norm
            st.session_state.valoraciones_norm = valoraciones_norm
            st.session_state.mercado_y = mercado_y
            st.session_state.mercado_q = mercado_q
            st.session_state.industrias_v = industrias_v
    else:
        nombre = st.session_state.nombre
        metricas_y = st.session_state.metricas_y
        metricas_q = st.session_state.metricas_q
        valoraciones_y = st.session_state.valoraciones_y
        valoraciones_q = st.session_state.valoraciones_q
        datos_norm = st.session_state.datos_norm
        valoraciones_norm = st.session_state.valoraciones_norm
        mercado_y = st.session_state.mercado_y
        mercado_q = st.session_state.mercado_q

    if ticker:
        empresa = nombre
        # SELECCIÓN DE DATOS
        data,valoraciones,x_column = get_company_data(metricas_y,metricas_q,valoraciones_y,valoraciones_q,period)


# HEADER
if ticker:
    mostrar_header(empresa,mercado_q)
    price_chart(mercado_q)
    if pantalla_carga:
        pantalla_carga.empty()

# NAVEGACIÓN
navigation()

# CONTENIDO
if ticker:
    mostrar_contenido(financial_section,financial_relational_charts,
    financial_market_relational_charts,calificacion_financiera,data,x_column,datos_norm,valoraciones,valoraciones_norm,metricas_y,period)

if pantalla_inicial:
    pantalla_inicial.empty()
    st.session_state.carga_inicial = False