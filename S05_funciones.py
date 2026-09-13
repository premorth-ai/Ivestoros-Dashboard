import numpy as np
import streamlit as st
from S04_graficos import financial_charts,financial_relational_charts,financial_market_relational_charts
from S02_datos import industrias
from S06_sistema_puntos import sistema_puntos

# DETERMINAR DIRECCION
def obtener_direccion(metric):
    if metric in ["debt_ebitda","debt_equity","ps","pe","pb","p_fcf"]:
        return "inverse"
    elif metric in ["capex"]:
        return "neutral"
    else:
        return "direct"

# DARLE FORMATO AL DATO ACTUAL
def formatear_valor(current,metric,percentage_metrics):
    if metric in percentage_metrics:
        return f"{current:.1%}"
    else:
        return f"{current:,.2f}".rstrip("0").rstrip(".")

# CALCULOS METRICAS FINANCIERAS
def calcular_evaluacion(data,metric):
    current = data[metric].iloc[-1]
    promedio = data[metric].mean()
    change_promedio = None
    change = None
    cagr = None
    change_antiguo = None
    if promedio != 0:
        change_promedio = (current - promedio) / promedio * 100
    if len(data) >= 2:
        previous = data[metric].iloc[-2]
        if previous != 0:
            change = (current - previous) / previous * 100
    if len(data) >= 2 and data[metric].iloc[0] != 0:
        cagr = (current / data[metric].iloc[0]) ** (1 / (len(data) - 1)) - 1
        change_antiguo = (current - data[metric].iloc[0]) / data[metric].iloc[0] * 100

    return {
        "promedio":change_promedio,
        "anterior":change,
        "cagr":cagr,
        "antiguo":change_antiguo
    }

# TENDENCIA
def calcular_tendencia(data,metric,cagr):
    tendencia = 0
    if len(data) >= 2:
        x = np.arange(len(data))
        y = data[metric].to_numpy()
        pendiente, intercepto = np.polyfit(x,y,1)
        regresion = pendiente * x + intercepto
        residuos = y - regresion
        suma_cuadrados_residuos = np.sum(residuos ** 2)
        suma_cuadrados_total = np.sum((y - np.mean(y)) ** 2)
        if suma_cuadrados_total != 0:
            r2 = 1 - (suma_cuadrados_residuos / suma_cuadrados_total)
        else:
            r2 = 0
        if r2 < 0.7 or cagr is None or abs(cagr) < 0.05:
            tendencia = 0
            nombre_tendencia = "Sin tendencia"
            texto_tendencia = ""
            arrow_tendencia = "—"
        else:
            if pendiente > 0:
                tendencia = 1
                nombre_tendencia = "Alcista"
                arrow_tendencia = "↑"
            elif pendiente < 0:
                tendencia = -1
                nombre_tendencia = "Bajista"
                arrow_tendencia = "↓"
            else:
                tendencia = 0
                nombre_tendencia = "Sin tendencia"
                arrow_tendencia = "—"
            if abs(cagr) > 0.10:
                texto_tendencia = "fuerte"
            else:
                texto_tendencia = ""

        return tendencia,nombre_tendencia,texto_tendencia,arrow_tendencia
    else:
        return tendencia,None,None,None

# CALCULOS VALORACIONES
def mostrar_valoracion(data,metric,current,direction):
    promedio = data[metric].mean()
    if promedio != 0:
        change_promedio = (current - promedio) / promedio * 100
        delta_promedio = f"{change_promedio:+.1f}%"
        if direction == "neutral":
            arrow_promedio = "↑" if change_promedio > 0 else "↓"
            delta_color_promedio = "gray"
        elif direction == "direct":
            arrow_promedio = "↑" if change_promedio > 0 else "↓"
            delta_color_promedio = "green" if change_promedio > 0 else "red"
        else:
            arrow_promedio = "↓" if change_promedio < 0 else "↑"
            delta_color_promedio = "green" if change_promedio < 0 else "red"
        st.markdown(f"Reciente vs promedio: <span style='color:{delta_color_promedio};'><strong>{arrow_promedio} {delta_promedio}</strong></span>",unsafe_allow_html=True)
    else:
        st.markdown("Reciente vs promedio: **N/A**")
    industria = st.session_state.industria
    datos_industria = obtener_industria(industria)
    if datos_industria is None:
        st.markdown("Reciente vs industria: **No has seleccionado una industria**")
        st.markdown("Reciente vs 5YA: **No has seleccionado una industria**")
    else:
        industria_actual = {"ps":"ps_actual","pe":"pe_actual","pb":"pb_actual","p_fcf":"pfcf_actual"}[metric]
        industria_5ya = {"ps":"ps_5ya","pe":"pe_5ya","pb":"pb_5ya","p_fcf":"pfcf_5ya"}[metric]
        valor_actual = datos_industria[industria_actual]
        valor_5ya = datos_industria[industria_5ya]
        if valor_actual != 0:
            change_industria = (current / valor_actual) - 1
            delta_industria = f"{change_industria:+.1%}"
            arrow_industria = "↓" if change_industria < 0 else "↑"
            delta_color_industria = "green" if change_industria < 0 else "red"
            st.markdown(f"Reciente vs industria: <span style='color:{delta_color_industria};'><strong>{arrow_industria} {delta_industria}</strong></span>",unsafe_allow_html=True)
        else:
            st.markdown("Reciente vs industria: **N/A**")
        if valor_5ya != 0:
            change_5ya = (current / valor_5ya) - 1
            delta_5ya = f"{change_5ya:+.1%}"
            arrow_5ya = "↓" if change_5ya < 0 else "↑"
            delta_color_5ya = "green" if change_5ya < 0 else "red"
            st.markdown(f"Reciente vs Industria 5YA: <span style='color:{delta_color_5ya};'><strong>{arrow_5ya} {delta_5ya}</strong></span>",unsafe_allow_html=True)
        else:
            st.markdown("Reciente vs Industria 5YA: **N/A**")

# TARJETAS DE MÉTRICAS
def metric_cards(data,metrics,percentage_metrics=None):
    percentage_metrics = percentage_metrics or []
    columnas = st.columns(len(metrics))
    es_valoracion = metrics == ["ps","pe","pb","p_fcf"]
    if "evaluaciones" not in data.attrs:
        data.attrs["evaluaciones"] = {}
    for columna,metric in zip(columnas,metrics):
        current = data[metric].iloc[-1]
        direction = obtener_direccion(metric)
        value = formatear_valor(current,metric,percentage_metrics)
        with columna:
            if es_valoracion:
                st.markdown(f"<strong>Dato reciente:</strong> {value}",unsafe_allow_html=True)
                with st.expander("Mostrar más"):
                    mostrar_valoracion(data,metric,current,direction)
            else:
                st.markdown(f"<strong>Dato actual:</strong> {value}",unsafe_allow_html=True)
                puntaje_placeholder = st.empty()
                with st.expander("Mostrar más"):
                    evaluacion = calcular_evaluacion(data,metric)
                    change_promedio = evaluacion["promedio"]
                    change = evaluacion["anterior"]
                    cagr = evaluacion["cagr"]
                    change_antiguo = evaluacion["antiguo"]
                    if change_promedio is not None:
                        delta_promedio = f"{change_promedio:+.1f}%"
                        if direction == "neutral":
                            arrow_promedio = "↑" if change_promedio > 0 else "↓"
                            delta_color_promedio = "gray"
                        elif direction == "direct":
                            arrow_promedio = "↑" if change_promedio > 0 else "↓"
                            delta_color_promedio = "green" if change_promedio > 0 else "red"
                        else:
                            arrow_promedio = "↓" if change_promedio > 0 else "↑"
                            delta_color_promedio = "green" if change_promedio < 0 else "red"
                        st.markdown(f"Reciente vs promedio: <span style='color:{delta_color_promedio};'><strong>{arrow_promedio} {delta_promedio}</strong></span>",unsafe_allow_html=True)
                    else:
                        st.markdown("Reciente vs promedio: **N/A**")
                    if change is not None:
                        delta = f"{change:+.1f}%"
                        if direction == "neutral":
                            arrow = "↑" if change > 0 else "↓"
                            delta_color = "gray"
                        elif direction == "direct":
                            arrow = "↑" if change > 0 else "↓"
                            delta_color = "green" if change > 0 else "red"
                        else:
                            arrow = "↓" if change < 0 else "↑"
                            delta_color = "green" if change < 0 else "red"
                        st.markdown(f"Reciente vs anterior: <span style='color:{delta_color};'><strong>{arrow} {delta}</strong></span>",unsafe_allow_html=True)
                    else:
                        st.markdown("Reciente vs anterior: **N/A**")
                    if cagr is not None:
                        cagr_value = f"{cagr:+.1%}"
                        if direction == "neutral":
                            arrow_cagr = "↑" if cagr > 0 else "↓"
                            delta_color_cagr = "gray"
                        elif direction == "direct":
                            arrow_cagr = "↑" if cagr > 0 else "↓"
                            delta_color_cagr = "green" if cagr > 0 else "red"
                        else:
                            arrow_cagr = "↓" if cagr < 0 else "↑"
                            delta_color_cagr = "green" if cagr < 0 else "red"
                        st.markdown(f"CAGR: <span style='color:{delta_color_cagr};'><strong>{arrow_cagr} {cagr_value}</strong></span>",unsafe_allow_html=True)
                    else:
                        st.markdown("CAGR: **N/A**")
                    if change_antiguo is not None:
                        delta_antiguo = f"{change_antiguo:+.1f}%"
                        if direction == "neutral":
                            arrow_antiguo = "↑" if change_antiguo > 0 else "↓"
                            delta_color_antiguo = "gray"
                        elif direction == "direct":
                            arrow_antiguo = "↑" if change_antiguo > 0 else "↓"
                            delta_color_antiguo = "green" if change_antiguo > 0 else "red"
                        else:
                            arrow_antiguo = "↓" if change_antiguo > 0 else "↑"
                            delta_color_antiguo = "green" if change_antiguo > 0 else "red"
                        st.markdown(f"Reciente vs el más antiguo: <span style='color:{delta_color_antiguo};'><strong>{arrow_antiguo} {delta_antiguo}</strong></span>",unsafe_allow_html=True)
                    else:
                        st.markdown("Reciente vs el más antiguo: **N/A**")
                    tendencia,nombre_tendencia,texto_tendencia,arrow_tendencia = calcular_tendencia(data,metric,cagr)
                    if len(data) >= 2:
                        if direction == "neutral":
                            color_tendencia = "gray"
                        elif tendencia > 0:
                            color_tendencia = "green"
                        elif tendencia < 0:
                            color_tendencia = "red"
                        else:
                            color_tendencia = "gray"
                        if texto_tendencia:
                            resultado_tendencia = f"{arrow_tendencia} {nombre_tendencia} {texto_tendencia}"
                        else:
                            resultado_tendencia = f"{arrow_tendencia} {nombre_tendencia}"
                        st.markdown(f"Tendencia: <span style='color:{color_tendencia};'><strong>{resultado_tendencia}</strong></span>",unsafe_allow_html=True)
                    else:
                        st.markdown("Tendencia: **N/A**")
                    data.attrs["evaluaciones"][metric] = {
                        "promedio":change_promedio,
                        "anterior":change,
                        "cagr":cagr,
                        "antiguo":change_antiguo,
                        "tendencia":tendencia
                    }
                if len(data) == 5:
                    puntajes = sistema_puntos(data)
                    st.session_state.puntajes_anuales = puntajes
                    if metric in puntajes:
                        puntaje_placeholder.markdown(f"<strong>Puntaje:</strong> {puntajes[metric]:.1f}/10",unsafe_allow_html=True)

# OBTENER INDUSTRIA
def obtener_industria(industria):
    if industria is None:
        return None
    datos_industria = industrias[industrias["industria"] == industria]
    if datos_industria.empty:
        return None
    return datos_industria.iloc[0]

# CALCULAR VALORACIONES
def calcular_valoraciones(data,industria):
    datos_industria = obtener_industria(industria)
    if datos_industria is None:
        return None

    metricas = {"ps":("ps_actual","ps_5ya"),"pe":("pe_actual","pe_5ya"),
                "pb":("pb_actual","pb_5ya"),"p_fcf":("pfcf_actual","pfcf_5ya")}
    resultados = {}
    for metrica,(industria_actual,industria_5ya) in metricas.items():
        empresa_actual = data[metrica].iloc[-1]
        if industria_actual != 0:
            diferencia_actual = (empresa_actual / datos_industria[industria_actual]) - 1
        else:
            diferencia_actual = None
        if industria_5ya != 0:
            diferencia_5ya = (empresa_actual / datos_industria[industria_5ya]) - 1
        else:
            diferencia_5ya = None
        resultados[metrica] = {"empresa": empresa_actual,"industria_actual": datos_industria[industria_actual],
            "industria_5ya": datos_industria[industria_5ya],"diferencia_actual": diferencia_actual,
            "diferencia_5ya": diferencia_5ya}
    return resultados

# SECCIONES FINANCIERAS INDIVIDUALES
def financial_section(data,x_column,title,metrics,percentage_metrics=None):
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>",unsafe_allow_html=True)
    financial_charts(data,x_column,metrics)
    metric_cards(data,metrics,percentage_metrics)

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

