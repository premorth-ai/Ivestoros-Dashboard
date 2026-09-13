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

# DETERMINAR COLOR
def obtener_color(valor,direction):
    if direction == "neutral":
        return "gray"
    if direction == "direct":
        return "green" if valor > 0 else "red"
    return "green" if valor < 0 else "red"

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
        valor_industria_actual = datos_industria[industria_actual]
        valor_industria_5ya = datos_industria[industria_5ya]
        if valor_industria_actual != 0:
            diferencia_actual = (empresa_actual / valor_industria_actual) - 1
        else:
            diferencia_actual = None
        if valor_industria_5ya != 0:
            diferencia_5ya = (empresa_actual / valor_industria_5ya) - 1
        else:
            diferencia_5ya = None
        resultados[metrica] = {"empresa":empresa_actual,"industria_actual":valor_industria_actual,
            "industria_5ya":valor_industria_5ya,"diferencia_actual": diferencia_actual,
            "diferencia_5ya": diferencia_5ya}
    return resultados

# TARJETAS DE MÉTRICAS
def metric_cards(data,metrics,percentage_metrics=None):
    percentage_metrics = percentage_metrics or []
    es_valoracion = metrics == ["ps","pe","pb","p_fcf"]
    if "evaluaciones" not in data.attrs:
        data.attrs["evaluaciones"] = {}
    resultados = {}
    valoraciones = calcular_valoraciones(data,st.session_state.industria) if es_valoracion else None
    for metric in metrics:
        current = data[metric].iloc[-1]
        direction = obtener_direccion(metric)
        value = formatear_valor(current,metric,percentage_metrics)
        if es_valoracion:
            resultados[metric] = {
                "current":current,
                "value":value,
                "direction":direction,
                "valoracion":valoraciones
            }
        else:
            evaluacion = calcular_evaluacion(data,metric)
            change_promedio = evaluacion["promedio"]
            change = evaluacion["anterior"]
            cagr = evaluacion["cagr"]
            change_antiguo = evaluacion["antiguo"]
            tendencia,nombre_tendencia,texto_tendencia,arrow_tendencia = calcular_tendencia(data,metric,cagr)
            data.attrs["evaluaciones"][metric] = {
                "promedio":change_promedio,
                "anterior":change,
                "cagr":cagr,
                "antiguo":change_antiguo,
                "tendencia":tendencia
            }
            resultados[metric] = {
                "current":current,
                "value":value,
                "direction":direction,
                "promedio":change_promedio,
                "anterior":change,
                "cagr":cagr,
                "antiguo":change_antiguo,
                "tendencia":tendencia,
                "nombre_tendencia":nombre_tendencia,
                "texto_tendencia":texto_tendencia,
                "arrow_tendencia":arrow_tendencia
            }
    if len(data) == 5 and not es_valoracion:
        puntajes = sistema_puntos(data)
        st.session_state.puntajes_anuales = puntajes
        for metric in metrics:
            if metric in puntajes:
                resultados[metric]["puntaje"] = puntajes[metric]
            else:
                resultados[metric]["puntaje"] = None
    else:
        for metric in metrics:
            resultados[metric]["puntaje"] = None
    return resultados

# SECCIONES FINANCIERAS INDIVIDUALES
def financial_section(data,x_column,title,metrics,percentage_metrics=None):
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>",unsafe_allow_html=True)
    resultados = metric_cards(data,metrics,percentage_metrics)
    graficos = financial_charts(data,x_column,metrics)
    columnas = st.columns(len(metrics))
    for columna,metric in zip(columnas,metrics):
        with columna:
            with st.container(border=True):
                label = {"ps":"Price/Sales","pe":"Price/Earnings","pb":"Price/Book","p_fcf":"Price/FCF",
                         "fcf":"FCF","fcf_margin":"FCF Margin"}.get(metric,metric.replace("_"," ").title())
                st.markdown(f"<h4 style='text-align: center;'>{label}</h4>",unsafe_allow_html=True)
                fig = graficos[metric]
                tab_grafico,tab_datos = st.tabs(["📊 Gráfico","📋 Datos"])
                with tab_grafico:
                    st.plotly_chart(fig,use_container_width=True,
                    config={"scrollZoom":False,"displayModeBar":True,"displaylogo":False,
                    "modeBarButtonsToRemove":["zoom2d","pan2d","select2d",
                    "lasso2d","zoomIn2d","zoomOut2d","autoScale2d","resetScale2d"],
                    "showTips":True})
                with tab_datos:
                    tabla_data = data[[x_column,metric]].set_index(x_column)
                    if metric in ["revenue","capex","fcf"]:
                        st.dataframe(tabla_data,use_container_width=True,
                            column_config={metric: st.column_config.NumberColumn(format="$%,.0f M")})
                    else:
                        st.dataframe(tabla_data,use_container_width=True)
                resultado = resultados[metric]
                if resultado["value"]:
                    if metric in ["ps","pe","pb","p_fcf"]:
                        st.markdown(f"<strong>Dato reciente:</strong> {resultado['value']}",unsafe_allow_html=True)
                    else:
                        st.markdown(f"<strong>Dato actual:</strong> {resultado['value']}",unsafe_allow_html=True)
                        if resultado["puntaje"] is not None:
                            st.markdown(f"<strong>Puntaje:</strong> {resultado['puntaje']:.1f}/10",unsafe_allow_html=True)
                with st.expander("Mostrar más"):
                    if metric in ["ps","pe","pb","p_fcf"]:
                        valoraciones = resultado["valoracion"]
                        if valoraciones is None:
                            st.markdown("Reciente vs industria: **No has seleccionado una industria**")
                            st.markdown("Reciente vs 5YA: **No has seleccionado una industria**")
                        else:
                            datos_valoracion = valoraciones[metric]
                            diferencia_actual = datos_valoracion["diferencia_actual"]
                            if diferencia_actual is not None:
                                arrow_actual = "↓" if diferencia_actual < 0 else "↑"
                                color_actual = "green" if diferencia_actual < 0 else "red"
                                st.markdown(f"Reciente vs industria: <span style='color:{color_actual};'><strong>{arrow_actual} {diferencia_actual:+.1%}</strong></span>",unsafe_allow_html=True)
                            else:
                                st.markdown("Reciente vs industria: **N/A**")
                            diferencia_5ya = datos_valoracion["diferencia_5ya"]
                            if diferencia_5ya is not None:
                                arrow_5ya = "↓" if diferencia_5ya < 0 else "↑"
                                color_5ya = "green" if diferencia_5ya < 0 else "red"
                                st.markdown(f"Reciente vs Industria 5YA: <span style='color:{color_5ya};'><strong>{arrow_5ya} {diferencia_5ya:+.1%}</strong></span>",unsafe_allow_html=True)
                            else:
                                st.markdown("Reciente vs Industria 5YA: **N/A**")
                    else:
                        change_promedio = resultado["promedio"]
                        change = resultado["anterior"]
                        cagr = resultado["cagr"]
                        change_antiguo = resultado["antiguo"]
                        tendencia = resultado["tendencia"]
                        nombre_tendencia = resultado["nombre_tendencia"]
                        texto_tendencia = resultado["texto_tendencia"]
                        arrow_tendencia = resultado["arrow_tendencia"]
                        if change_promedio is not None:
                            color_promedio = obtener_color(change_promedio,resultado["direction"])
                            st.markdown(f"Reciente vs promedio: <span style='color:{color_promedio};'><strong>{change_promedio:+.1f}%</strong></span>",unsafe_allow_html=True)
                        else:
                            st.markdown("Reciente vs promedio: **N/A**")
                        if change is not None:
                            color_anterior = obtener_color(change,resultado["direction"])
                            st.markdown(f"Reciente vs anterior: <span style='color:{color_anterior};'><strong>{change:+.1f}%</strong></span>",unsafe_allow_html=True)
                        else:
                            st.markdown("Reciente vs anterior: **N/A**")
                        if cagr is not None:
                            color_cagr = obtener_color(cagr,resultado["direction"])
                            st.markdown(f"CAGR: <span style='color:{color_cagr};'><strong>{cagr:+.1%}</strong></span>",unsafe_allow_html=True)
                        else:
                            st.markdown("CAGR: **N/A**")
                        if change_antiguo is not None:
                            color_antiguo = obtener_color(change_antiguo,resultado["direction"])
                            st.markdown(f"Reciente vs el más antiguo: <span style='color:{color_antiguo};'><strong>{change_antiguo:+.1f}%</strong></span>",unsafe_allow_html=True)
                        else:
                            st.markdown("Reciente vs el más antiguo: **N/A**")
                        if len(data) >= 2:
                            if resultado["direction"] == "neutral":
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