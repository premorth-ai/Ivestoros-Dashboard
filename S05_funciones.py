import streamlit as st

# SECCIONES FINANCIERAS INDIVIDUALES
def seccion_financiera(data, x_column, title, metrics, metricas_y, period):
    from S04_graficos import graficos_metricas, graficos_valoraciones
    
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
    if title == "Valoraciones":
        graficos_valoraciones(data, x_column, metrics)
    else:
        calculos = {metric: calcular_metricas(metricas_y, metric) for metric in metrics}
        calificaciones = sistema_calificacion(metricas_y)
        graficos_metricas(data, x_column, metrics, calculos,calificaciones,comparar_trimestrales,formato_color,formato_calificacion,formato_trimestrales)

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
        "CAGR": ((actual / antiguo) ** (1 / (len(metricas_y) - 1)) - 1) * 100}
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
        "Empresa vs S&P 500": (actual / sp500 - 1) * 100}
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

# COMPARAR TRIMESTRALES
def comparar_trimestrales(metricas_q, metricas_y, metric):
    ultimo_periodo = metricas_y.iloc[:, 0].iloc[-1]
    periodo_q4 = ultimo_periodo.replace("FY", "Q4")
    posicion_q4 = metricas_q.index[metricas_q.iloc[:, 0] == periodo_q4][0]
    datos_posteriores = metricas_q.loc[posicion_q4:, metric].dropna()
    datos_posteriores = datos_posteriores.iloc[1:]
    if len(datos_posteriores) == 0:
        return "No hay nuevos trimestres"
    if len(datos_posteriores) >= 4:
        return "No hay nuevos trimestres"
    dato_q4 = metricas_q.loc[posicion_q4, metric]
    if len(datos_posteriores) == 1:
        dato_comparar = datos_posteriores.iloc[0]
    else:
        dato_comparar = datos_posteriores.mean()
    if dato_comparar > dato_q4:
        return "Trimestrales creciendo"
    elif dato_comparar < dato_q4:
        return "Trimestrales decreciendo"
    return "Trimestrales estables"

# FORMATO COLOR TRIMESTRALES
def formato_trimestrales(metric, tendencia):
    metricas_inversas = {"Debt/Equity","Debt/EBITDA"}
    if tendencia == "Trimestrales creciendo":
        if metric in metricas_inversas:
            return "<b style='color: red;'>Trimestrales creciendo</b>"
        return "<b style='color: green;'>Trimestrales creciendo</b>"
    if tendencia == "Trimestrales decreciendo":
        if metric in metricas_inversas:
            return "<b style='color: green;'>Trimestrales decreciendo</b>"
        return "<b style='color: red;'>Trimestrales decreciendo</b>"
    return f"<b>{tendencia}</b>"

# Formato de color
def formato_color(metric, calculo):
    metricas_directas = {"Revenue","FCF","Operating Margin","ROIC","FCF margin", "Current ratio"}
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
    """
    st.markdown(mensaje, unsafe_allow_html=True)

def formato_calificacion(calificacion):
    if calificacion < 5:
        return f"<b style='color: red;'>{calificacion:.1f}/10</b>"
    if calificacion <= 7:
        return f"<b style='color: #E6B800;'>{calificacion:.1f}/10</b>"
    return f"<b style='color: green;'>{calificacion:.1f}/10</b>"

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
    if "industria" not in st.session_state:
        st.session_state.industria = None
    if "sector" not in st.session_state:
        st.session_state.sector = None

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
    datos_norm["EBITDA/Debt"] = datos_norm["Debt/EBITDA"].apply(lambda x: 1 / x if x != 0 else 0)
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

# SISTEMA DE PUNTOS
def sistema_calificacion(metricas_y):
    calificaciones = {}
    rangos = {
    "Revenue": [(0.15,10),(0.11,9),(0.08,8),(0.05,7),(0.02,6),(0,5),(-0.05,4),(-0.10,3),(-0.20,2)],
    "FCF": [(0.25,10),(0.18,9),(0.12,8),(0.07,7),(0.03,6),(-0.03,5),(-0.10,4),(-0.20,3),(-0.35,2)],
    "Operating Margin": [(0.30,10),(0.20,9),(0.15,8),(0.10,7),(0.07,6),(0.05,5),(0.04,4),(0.03,3),(0,2)],
    "ROIC": [(0.30,10),(0.20,9),(0.15,8),(0.10,7),(0.07,6),(0.05,5),(0.04,4),(0.03,3),(0,2)],
    "FCF margin": [(0.225,10),(0.15,9),(0.10,8),(0.07,7),(0.05,6),(0.04,5),(0.03,4),(0.02,3),(0,2)],
    "Debt/Equity": [(0.2,10),(0.4,9),(0.6,8),(0.8,7),(1.0,6),(1.4,5),(1.8,4),(2.2,3),(3.0,2)],
    "Debt/EBITDA": [(0.5,10),(1.0,9),(1.5,8),(2.0,7),(2.5,6),(3.0,5),(3.5,4),(4.0,3),(5.0,2)],
    "Current ratio": [(2.5,10),(2.2,9),(1.9,8),(1.6,7),(1.3,6),(1.1,5),(0.9,4),(0.7,3),(0.5,2)]
    }
    menor_es_mejor = {"Debt/Equity","Debt/EBITDA"}
    for metric, rangos_metric in rangos.items():
        datos = metricas_y[metric].dropna()
        if datos.empty:
            calificaciones[metric] = None
            continue
        if metric in {"Revenue","FCF"}:
            valor = ((datos.iloc[-1] / datos.iloc[0]) ** (1 / (len(datos) - 1)) - 1)
        else:
            valor = datos.iloc[-1]
        for umbral, calificacion in rangos_metric:
            if metric in menor_es_mejor:
                if valor <= umbral:
                    calificaciones[metric] = calificacion
                    break
            elif valor >= umbral:
                calificaciones[metric] = calificacion
                break
        else:
            calificaciones[metric] = 0

    return calificaciones

# CALIFICACIÓN FINANCIERA
def calificacion_financiera(metricas_y):
    puntos = sistema_calificacion(metricas_y)
    crecimiento = (puntos["Revenue"] + puntos["FCF"]) / 2
    rentabilidad = (puntos["Operating Margin"] + puntos["ROIC"] + puntos["FCF margin"]) / 3
    solidez = (puntos["Debt/Equity"] + puntos["Debt/EBITDA"] + puntos["Current ratio"]) / 3
    total = (crecimiento + rentabilidad + solidez) / 3
    metricas_mejorar = [
        f"{metric}: {puntos[metric]}/10"
        for metric in puntos
        if puntos[metric] < 7]
    if not metricas_mejorar:
        metricas_mejorar = ["Todas las métricas están en un nivel competente."]
    return {
        "Puntos": puntos,"Crecimiento": crecimiento,"Rentabilidad": rentabilidad,"Solidez financiera": solidez,
        "Total": total,"Métricas a mejorar": metricas_mejorar}