import streamlit as st
import plotly.express as px

color = "#2C3490"

def configurar_grafico(fig,altura=400):
    fig.update_layout(height=altura,xaxis_title=None,yaxis_title=None,dragmode=False)
    if fig.data[0].type == "scatter":
        fig.update_traces(line=dict(width=3))

def mostrar_grafico(fig):
    st.plotly_chart(fig,use_container_width=True,
    config={"scrollZoom":False,"displayModeBar":True,"displaylogo":False,
    "modeBarButtonsToRemove":["zoom2d","pan2d","select2d",
    "lasso2d","zoomIn2d","zoomOut2d","autoScale2d","resetScale2d"],
    "showTips":True})

# GRAFICO PRECIO POR PERIODO
def price_chart(data,x_column,precio_actual):
    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Precio por periodo</h4>",unsafe_allow_html=True)
        chart_data = data[[x_column,"precio"]]
        chart_data[x_column] = chart_data[x_column].astype(str)
        chart_data.loc[len(chart_data)] = ["Actual",precio_actual]
        tab_grafico,tab_datos = st.tabs(["📊 Gráfico","📋 Datos"])
        with tab_grafico:
            fig = px.line(chart_data,x=x_column,y="precio",markers=True)
            configurar_grafico(fig)
            mostrar_grafico(fig)
        with tab_datos:
            tabla_data = chart_data
            st.dataframe(tabla_data,use_container_width=True)

# GRÁFICOS POR COMPONENTES
def financial_charts(data,x_column,metrics):
    columns = st.columns(len(metrics))
    for column,metric in zip(columns,metrics):
        with column:
            with st.container(border=True):
                chart_data = data[[x_column,metric]].set_index(x_column)
                label = {"ps":"Price/Sales","pe":"Price/Earnings","pb":"Price/Book","p_fcf":"Price/FCF",
                         "fcf":"FCF","fcf_margin":"FCF Margin"}.get(metric,metric.replace("_"," ").title())
                st.markdown(f"<h4 style='text-align: center;'>{label}</h4>",unsafe_allow_html=True)
                tab_grafico,tab_datos = st.tabs(["📊 Gráfico","📋 Datos"])
                with tab_grafico:
                    fig = px.bar(chart_data,x=chart_data.index,y=metric,color_discrete_sequence=[color])
                    fig.update_traces(marker_line_width=1,marker_line_color="#000000")
                    if metric in ["revenue","capex","fcf"]:
                        fig.update_traces(hovertemplate="$%{y:,.0f} M<extra></extra>")
                    else:
                        fig.update_traces(hovertemplate="%{y:,.2f}<extra></extra>")
                    configurar_grafico(fig,300)
                    fig.update_xaxes(type="category",tickmode="array",tickvals=chart_data.index.tolist())
                    mostrar_grafico(fig)
                with tab_datos:
                    tabla_data = chart_data
                    if metric in ["revenue","capex","fcf"]:
                        st.dataframe(tabla_data,use_container_width=True,
                            column_config={metric: st.column_config.NumberColumn(format="$%,.0f M")})
                    else:
                        st.dataframe(tabla_data,use_container_width=True)

# GRÁFICOS FINANCIEROS
def financial_relational_charts(datos_norm):
    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Revenue vs FCF vs CapEx</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","revenue","fcf","capex"]]
        fig = px.line(chart_data,x="fiscal_year",y=["revenue","fcf","capex"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A","#329356"])
        configurar_grafico(fig)
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Operating Margin vs ROIC vs CapEx</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","operating_margin","roic","capex"]]
        fig = px.line(chart_data,x="fiscal_year",y=["operating_margin","roic","capex"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A","#329356"])
        configurar_grafico(fig)
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Revenue vs Operating Margin vs EBITDA/Deuda</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","revenue","operating_margin","ebitda_deuda"]]
        fig = px.line(chart_data,x="fiscal_year",y=["revenue","operating_margin","ebitda_deuda"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A","#329356"])
        configurar_grafico(fig)
        mostrar_grafico(fig)

# GRÁFICOS BURSÁTIL FINANCIEROS
def financial_market_relational_charts(datos_norm):
    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/E vs EBITDA/Deuda</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","pe","ebitda_deuda"]]
        fig = px.line(chart_data,x="fiscal_year",y=["pe","ebitda_deuda"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A"])
        configurar_grafico(fig)
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/S vs Operating Margin</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","ps","operating_margin"]]
        fig = px.line(chart_data,x="fiscal_year",y=["ps","operating_margin"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A"])
        configurar_grafico(fig)
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/B vs Debt/Equity</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","pb","debt_equity"]]
        fig = px.line(chart_data,x="fiscal_year",y=["pb","debt_equity"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A"])
        configurar_grafico(fig)
        mostrar_grafico(fig)

    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>P/FCF vs Current Ratio</h4>",unsafe_allow_html=True)
        chart_data = datos_norm[["fiscal_year","p_fcf","current_ratio"]]
        fig = px.line(chart_data,x="fiscal_year",y=["p_fcf","current_ratio"],markers=True,
        color_discrete_sequence=["#2382CA","#533F8A"])
        configurar_grafico(fig)
        mostrar_grafico(fig)