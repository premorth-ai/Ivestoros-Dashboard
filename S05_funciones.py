import streamlit as st

# SECCIONES FINANCIERAS INDIVIDUALES
def financial_section(data, x_column, title, metrics, metricas_y, period):
    # Carga diferida para evitar el bucle circular con S04_graficos
    from S04_graficos import financial_metric_charts, financial_valuation_charts
    
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
    if title == "Valoraciones":
        financial_valuation_charts(data, x_column, metrics)
    else:
        calculos = {metric: calcular_metricas(metricas_y, metric) for metric in metrics}
        financial_metric_charts(data, x_column, metrics, calculos, period)

# CÁLCULO DE MÉTRICAS
def calcular_metricas(metricas_y, metric):
    actual = metricas_y[metric].iloc[-1]
    anterior = metricas_y[metric].iloc[-2]
    antiguo = metricas_y[metric].iloc[0]
    promedio_5ya = metricas_y[metric].iloc[:-1].mean()
    resultados = {
        "Actual vs anterior": (actual / anterior - 1) * 100,
        "Actual vs más antiguo": (actual / antiguo - 1) * 100,
        "Actual vs 5YA": (actual / promedio_5ya - 1) * 100,
        "CAGR": ((actual / antiguo) ** (1 / (len(metricas_y) - 1)) - 1) * 100
    }
    return resultados

def determinar_tendencia(metricas_q, metric):
    datos = metricas_q[metric].dropna()
    antiguo = datos.iloc[0]
    actual = datos.iloc[-1]

    # Descarte directo si son iguales o si el dato inicial es 0
    if actual == antiguo or antiguo == 0:
        return "Lateral / No Definida"

    cambio_global = (actual - antiguo) / abs(antiguo)
    variaciones = datos.pct_change().dropna()
    total_variaciones = len(variaciones)
    umbral_16 = max(1, int(total_variaciones * 0.68)) # ~13 de 19

    # ----------------------------------------------------
    # TENDENCIA ALCISTA
    # ----------------------------------------------------
    if cambio_global >= 0.30:
        cumple_pasos = (variaciones >= 0.02).sum() >= umbral_16
        pos_fallas = [i for i, v in enumerate(variaciones) if v < 0.02]
        tiene_caida_grave = any(variaciones.iloc[i] < -0.2 for i in pos_fallas)
        consecutivas = len(pos_fallas) > 1 and any(pos_fallas[i+1] - pos_fallas[i] == 1 for i in range(len(pos_fallas)-1))
        
        if cumple_pasos and (not tiene_caida_grave) and (not consecutivas):
            return "Alcista"

    # ----------------------------------------------------
    # TENDENCIA BAJISTA
    # ----------------------------------------------------
    elif cambio_global < -0.30:
        cumple_pasos = (variaciones <= -0.02).sum() >= umbral_16
        pos_fallas = [i for i, v in enumerate(variaciones) if v > -0.02]
        tiene_rebote_grave = any(variaciones.iloc[i] > 0.2 for i in pos_fallas)
        consecutivas = len(pos_fallas) > 1 and any(pos_fallas[i+1] - pos_fallas[i] == 1 for i in range(len(pos_fallas)-1))
        
        if cumple_pasos and (not tiene_rebote_grave) and (not consecutivas):
            return "Bajista"

    return "Lateral / No Definida"

# SELECCIÓN DE DATOS
def get_company_data(metricas_y, metricas_q, valoraciones_y, valoraciones_q, period):
    if period == "Fiscal Year":
        return metricas_y.copy(), valoraciones_y.copy(), "Fiscal Year"
    return metricas_q.copy(), valoraciones_q.copy(), "Fiscal Quarter"

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

# NORMALIZAR DATOS BASE 100 (Con validación contra división por cero)
def normalizar_datos(datos_y, valoraciones_y):
    datos_norm = datos_y.copy()
    valoraciones_norm = valoraciones_y.copy()
    
    # Inverso seguro para Debt/EBITDA
    datos_norm["Debt/EBITDA Inverso"] = datos_norm["Debt/EBITDA"].apply(lambda x: 1 / x if x != 0 else 0)
    
    for columna in datos_norm.columns[1:]:
        val_inicial = datos_norm[columna].iloc[0]
        if val_inicial != 0:
            datos_norm[columna] = (datos_norm[columna] / val_inicial) * 100
        else:
            datos_norm[columna] = 0

    for columna in valoraciones_norm.columns[1:]:
        val_inicial = valoraciones_norm[columna].iloc[0]
        if val_inicial != 0:
            valoraciones_norm[columna] = (valoraciones_norm[columna] / val_inicial) * 100
        else:
            valoraciones_norm[columna] = 0

    return datos_norm, valoraciones_norm