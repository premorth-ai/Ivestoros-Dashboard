import streamlit as st
import plotly.express as px

color = "#2C3490"

def configurar_grafico(fig, altura=400):
    fig.update_layout(height=altura, xaxis_title=None, yaxis_title=None, dragmode=False)
    if fig.data[0].type == "scatter":
        fig.update_traces(line=dict(width=3))

def mostrar_grafico(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,"displayModeBar": True,"displaylogo": False,"modeBarButtonsToRemove": [
            "zoom2d", "pan2d", "select2d","lasso2d", "zoomIn2d", "zoomOut2d","autoScale2d", "resetScale2d"],
            "showTips": True})

# GRAFICO PRECIO POR PERIODO
def price_chart(data):
    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Precio por periodo</h4>", unsafe_allow_html=True)
        chart_data = data[["Fiscal Quarter", "Precio"]].copy()
        chart_data["Fiscal Quarter"] = chart_data["Fiscal Quarter"].astype(str).str.replace("Q4", "FY", regex=False)
        tab_grafico, tab_datos = st.tabs(["📊 Gráfico", "📋 Datos"])
        with tab_grafico:
            fig = px.line(chart_data, x="Fiscal Quarter", y="Precio", markers=True)
            fig.update_xaxes(
                tickmode="array",
                tickvals=chart_data["Fiscal Quarter"],
                ticktext=[
                    f"<b>{x}</b>" if x in ["FY", "Actual"] else x
                    for x in chart_data["Fiscal Quarter"]])
            configurar_grafico(fig)
            mostrar_grafico(fig)
            actual = data[data["Fiscal Quarter"] == "Actual"].iloc[0]
            st.markdown(f"**Precio último cierre:** ${actual['Precio']}")
            st.markdown(f"**Market Cap último cierre:** {actual['Marketcap']/1000:,.2f} B")
        with tab_datos:
            tabla_data = chart_data
            st.dataframe(tabla_data, use_container_width=True)

# GRÁFICOS DE MÉTRICAS
def graficos_metricas(metricas, x_column, metrics, calculos,calificaciones,determinar_tendencia,mostrar_evaluacion,formato_calificacion,formato_trimestrales):
    columnas = st.columns(len(metrics))
    for columna, metric in zip(columnas, metrics):
        with columna:
            with st.container(border=True):
                label = {"FCF": "FCF", "FCF margin": "FCF Margin"}.get(metric, metric.replace("_", " ").title())
                st.markdown(f"<h4 style='text-align: center;'>{label}</h4>", unsafe_allow_html=True)
                chart_data = metricas[[x_column, metric]].set_index(x_column)
                fig = px.bar(chart_data, x=chart_data.index, y=metric, color_discrete_sequence=[color])
                fig.update_traces(marker_line_width=1, marker_line_color="#000000")
                if metric in ["Revenue", "CapEx", "FCF"]:
                    fig.update_traces(hovertemplate="$%{y:,.0f} M<extra></extra>")
                elif metric in ["Operating Margin", "FCF margin", "ROIC"]:
                    fig.update_traces(hovertemplate="%{y:,.2f}%<extra></extra>")
                else:
                    fig.update_traces(hovertemplate="%{y:,.2f}<extra></extra>")
                configurar_grafico(fig, 300)
                fig.update_xaxes(type="category", tickmode="array", tickvals=chart_data.index.tolist())

                tab_grafico, tab_datos = st.tabs(["📊 Gráfico", "📋 Datos"])
                with tab_grafico:
                    mostrar_grafico(fig)
                with tab_datos:
                    tabla_data = metricas[[x_column, metric]].set_index(x_column)
                    if metric in ["Revenue", "CapEx", "FCF"]:
                        st.dataframe(tabla_data, use_container_width=True,
                                    column_config={metric: st.column_config.NumberColumn(format="$%,.0f M")})
                    elif metric in ["Operating Margin", "FCF margin", "ROIC"]:
                        st.dataframe(tabla_data, use_container_width=True,
                                    column_config={metric: st.column_config.NumberColumn(format="%.2f%%")})
                    else:
                        st.dataframe(tabla_data, use_container_width=True)

                dato_actual = metricas[metric].iloc[-1]
                if metric in ["Revenue", "CapEx", "FCF"]:
                    st.markdown(f"**Dato Actual:** ${dato_actual:,.0f} M")
                elif metric in ["Operating Margin", "FCF margin", "ROIC"]:
                    st.markdown(f"**Dato Actual:** {dato_actual:,.2f}%")
                else:
                    st.markdown(f"**Dato Actual:** {dato_actual:,.2f}")
                if metric == "CapEx":
                    st.markdown("**Calificación:** No aplica")
                else:
                    calificacion = formato_calificacion(calificaciones[metric])
                    st.markdown(f"**Calificación:** {calificacion}", unsafe_allow_html=True)
                tendencia = determinar_tendencia(st.session_state.metricas_q, st.session_state.metricas_y, metric)
                tendencia = formato_trimestrales(metric, tendencia)
                st.markdown(f"**Tendencia:** {tendencia}", unsafe_allow_html=True)
                with st.expander("Mostrar más"):
                    mostrar_evaluacion(metric, calculos[metric])

# GRÁFICOS DE VALORACIONES
def graficos_valoraciones(valoraciones, x_column, metrics):
    from S05_funciones import industrias
    columnas = st.columns(2)
    for i, metric in enumerate(metrics):
        with columnas[i % 2]:
            with st.container(border=True):
                label = {"P/S": "Price/Sales", "P/E": "Price/Earnings", "P/B": "Price/Book", "P/FCF": "Price/FCF"}.get(metric, metric.replace("_", " ").title())
                st.markdown(f"<h4 style='text-align: center;'>{label}</h4>", unsafe_allow_html=True)
                chart_data = valoraciones[[x_column, metric]].set_index(x_column)
                fig = px.bar(chart_data, x=chart_data.index, y=metric, color_discrete_sequence=[color])
                fig.update_traces(marker_line_width=1, marker_line_color="#000000")
                fig.update_traces(hovertemplate="%{y:,.2f}<extra></extra>")
                configurar_grafico(fig, 300)
                fig.update_xaxes(type="category", tickmode="array", tickvals=chart_data.index.tolist())
                tab_grafico, tab_datos = st.tabs(["📊 Gráfico", "📋 Datos"])
                with tab_grafico:
                    mostrar_grafico(fig)
                with tab_datos:
                    tabla_data = valoraciones[[x_column, metric]].set_index(x_column)
                    st.dataframe(tabla_data, use_container_width=True)
                dato_actual = valoraciones[metric].iloc[-1]
                st.markdown(f"**Dato Actual:** {dato_actual:,.2f}")
                with st.expander("Mostrar más"):
                    industrias(st.session_state.valoraciones_y,metric,st.session_state.industrias_v)

# GRÁFICOS FINANCIEROS
def graficos_relaciones_metricas(datos_norm):
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Relaciones financieras (datos normalizados)</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Calidad crecimiento</h4>", unsafe_allow_html=True)
        chart_data = datos_norm[["Fiscal Year", "Revenue", "FCF", "CapEx"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["Revenue", "FCF", "CapEx"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A", "#329356"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Calidad rentabilidad</h4>", unsafe_allow_html=True)
        chart_data = datos_norm[["Fiscal Year", "Operating Margin", "ROIC", "CapEx"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["Operating Margin", "ROIC", "CapEx"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A", "#329356"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Solvencia financiera</h4>", unsafe_allow_html=True)
        chart_data = datos_norm[["Fiscal Year", "FCF", "Operating Margin", "EBITDA/Debt"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["FCF", "Operating Margin", "EBITDA/Debt"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A", "#329356"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Liquidez financiera</h4>", unsafe_allow_html=True)
        chart_data = datos_norm[["Fiscal Year", "FCF", "FCF margin", "Current ratio"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["FCF", "FCF margin", "Current ratio"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A", "#329356"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Apalancamiento</h4>", unsafe_allow_html=True)
        chart_data = datos_norm[["Fiscal Year", "Revenue", "ROIC", "Debt/Equity"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["Revenue", "ROIC", "Debt/Equity"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A", "#329356"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

# GRÁFICOS BURSÁTIL FINANCIEROS
def graficos_relaciones_valoraciones(datos_norm, valoraciones_norm):
    datos = datos_norm.merge(valoraciones_norm, on="Fiscal Year")
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Relaciones Bursátiles (Datos normalizados)</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/E vs EBITDA/Deuda</h4>", unsafe_allow_html=True)
        chart_data = datos[["Fiscal Year", "P/E", "EBITDA/Debt"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["P/E", "EBITDA/Debt"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/S vs Operating Margin</h4>", unsafe_allow_html=True)
        chart_data = datos[["Fiscal Year", "P/S", "Operating Margin"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["P/S", "Operating Margin"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/B vs Debt/Equity</h4>", unsafe_allow_html=True)
        chart_data = datos[["Fiscal Year", "P/B", "Debt/Equity"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["P/B", "Debt/Equity"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/FCF vs FCF Margin</h4>", unsafe_allow_html=True)
        chart_data = datos[["Fiscal Year", "P/FCF", "FCF margin"]]
        fig = px.line(chart_data, x="Fiscal Year", y=["P/FCF", "FCF margin"], markers=True,
                      color_discrete_sequence=["#2382CA", "#533F8A"])
        configurar_grafico(fig)
        fig.update_yaxes(type="log")
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        mostrar_grafico(fig)