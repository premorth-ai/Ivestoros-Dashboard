import streamlit as st

# SECCIONES FINANCIERAS INDIVIDUALES
def financial_section(data, x_column, title, metrics, metricas_y, period):
    # Carga diferida para evitar el bucle circular con S04_graficos
    from S04_graficos import financial_metric_charts, financial_valuation_charts
    from S06_sistema_puntos import sistema_puntos
    
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
    if title == "Valoraciones":
        financial_valuation_charts(data, x_column, metrics)
    else:
        calculos = {metric: calcular_metricas(metricas_y, metric) for metric in metrics}
        calificaciones = sistema_puntos(metricas_y)
        financial_metric_charts(data, x_column, metrics, calculos,calificaciones,determinar_tendencia,mostrar_evaluacion)

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

# COMPARACIÓN CON INDUSTRIA
def industrias(valoraciones_y, metric, industrias_v):
    actual = valoraciones_y[metric].iloc[-1]
    promedio_5ya = valoraciones_y[metric].iloc[:-1].mean()
    industria = industrias_v.loc[industrias_v.iloc[:, 0] == "Industry", metric].iloc[0]
    sector = industrias_v.loc[industrias_v.iloc[:, 0] == "Sector", metric].iloc[0]
    sp500 = industrias_v.loc[industrias_v.iloc[:, 0] == "S&P 500", metric].iloc[0]

    comparaciones = {
        "Empresa vs 5YA": (actual / promedio_5ya - 1) * 100,
        "Empresa vs Industry": (actual / industria - 1) * 100,
        "Empresa vs Sector": (actual / sector - 1) * 100,
        "Empresa vs S&P 500": (actual / sp500 - 1) * 100
    }

    mensaje = ""

    for nombre, valor in comparaciones.items():
        if valor < 0:
            resultado = f"<b style='color: green;'>↓ {abs(valor):,.2f}%</b>"
        elif valor > 0:
            resultado = f"<b style='color: red;'>↑ {valor:,.2f}%</b>"
        else:
            resultado = "<b>→ 0.00%</b>"

        mensaje += f"**{nombre}:** {resultado}<br>"

    st.markdown(mensaje, unsafe_allow_html=True)

# Tendencia
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

    # TENDENCIA ALCISTA
    if cambio_global >= 0.30:
        cumple_pasos = (variaciones >= 0.02).sum() >= umbral_16
        pos_fallas = [i for i, v in enumerate(variaciones) if v < 0.02]
        tiene_caida_grave = any(variaciones.iloc[i] < -0.2 for i in pos_fallas)
        tres_consecutivas = len(pos_fallas) > 2 and any(
        pos_fallas[i + 2] - pos_fallas[i] == 2 and pos_fallas[i + 1] - pos_fallas[i] == 1
        for i in range(len(pos_fallas) - 2)
                                        )
        
        if cumple_pasos and (not tiene_caida_grave) and (not tres_consecutivas):
            return "Alcista"

    # TENDENCIA BAJISTA
    elif cambio_global < -0.30:
        cumple_pasos = (variaciones <= -0.02).sum() >= umbral_16
        pos_fallas = [i for i, v in enumerate(variaciones) if v > -0.02]
        tiene_rebote_grave = any(variaciones.iloc[i] > 0.2 for i in pos_fallas)
        tres_consecutivas = len(pos_fallas) > 2 and any(
        pos_fallas[i + 2] - pos_fallas[i] == 2 and pos_fallas[i + 1] - pos_fallas[i] == 1
        for i in range(len(pos_fallas) - 2)
                                        )
        
        if cumple_pasos and (not tiene_rebote_grave) and (not tres_consecutivas):
            return "Bajista"

    return "Lateral / No Definida"

# MOSTRAR EVALUACIÓN
def mostrar_evaluacion(metric, calculo, tendencia):
    metricas_directas = {"Revenue","FCF","Operating Margin","ROIC","FCF margin"}
    metricas_inversas = {"Debt/Equity","Debt/EBITDA"}

    def formato(valor):
        if metric in metricas_directas:
            if valor > 0:
                return f"<b style='color: green;'>↑ {valor:,.2f}%</b>"
            elif valor < 0:
                return f"<b style='color: red;'>↓ {abs(valor):,.2f}%</b>"
            return f"<b>→ 0.00%</b>"

        if metric in metricas_inversas:
            if valor < 0:
                return f"<b style='color: green;'>↓ {abs(valor):,.2f}%</b>"
            elif valor > 0:
                return f"<b style='color: red;'>↑ {valor:,.2f}%</b>"
            return f"<b>→ 0.00%</b>"

        if valor > 0:
            return f"<b>↑ {valor:,.2f}%</b>"
        elif valor < 0:
            return f"<b>↓ {abs(valor):,.2f}%</b>"
        return f"<b>→ 0.00%</b>"

    mensaje = f"""
    **Actual vs anterior:** {formato(calculo["Actual vs anterior"])}  
    **Actual vs más antiguo:** {formato(calculo["Actual vs más antiguo"])}  
    **Actual vs promedio:** {formato(calculo["Actual vs 5YA"])}  
    **CAGR:** {formato(calculo["CAGR"])}  
    **Tendencia:** {tendencia}
    """

    st.markdown(mensaje, unsafe_allow_html=True)

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
    if "industrias_v" not in st.session_state:
        st.session_state.industrias_v = None

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