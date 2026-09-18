import pandas as pd
import requests
from io import StringIO
from concurrent.futures import ThreadPoolExecutor

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}

# CONSULTA A STOCK ANALISYS
def consultar_web(ticker):
    # VALIDAR TICKER
    url = f"https://stockanalysis.com/stocks/{ticker}/"
    respuesta = requests.get(url, headers=headers)
    
    if respuesta.status_code != 200:
        return None

    # OBTENER NOMBRE
    posicion = respuesta.text.find('"@type":"Corporation"')
    bloque = respuesta.text[posicion:posicion+100]
    inicio = bloque.find('"name":"') + 8
    fin = bloque.find('"',inicio)
    nombre = bloque[inicio:fin]

    urls_y = [
        f"https://stockanalysis.com/stocks/{ticker}/financials/income-statement/",
        f"https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/",
        f"https://stockanalysis.com/stocks/{ticker}/financials/ratios/"
    ]
    urls_q = [
        f"https://stockanalysis.com/stocks/{ticker}/financials/income-statement/?p=quarterly",
        f"https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/?p=quarterly",
        f"https://stockanalysis.com/stocks/{ticker}/financials/ratios/?p=quarterly"
    ]

    # DATOS QUE QUEREMOS ENCONTRAR
    datos_buscar = ["Revenue","Capital Expenditures","Free Cash Flow","Operating Margin",
        "Return on Invested Capital (ROIC)","Free Cash Flow Margin","Current Ratio",
        "Debt / EBITDA Ratio","Debt / Equity Ratio","PS Ratio","PE Ratio","PB Ratio","P/FCF Ratio",
        "Last Close Price", "Market Capitalization"]

    # CAMBIAR NOMBRES
    nombres_columnas = {
        "Return on Invested Capital (ROIC)": "ROIC","Capital Expenditures": "CapEx",
        "Free Cash Flow": "FCF","Free Cash Flow Margin": "FCF margin","Debt / EBITDA Ratio": "Debt/EBITDA",
        "Debt / Equity Ratio": "Debt/Equity","Current Ratio": "Current ratio","PS Ratio": "P/S",
        "PE Ratio": "P/E","PB Ratio": "P/B","P/FCF Ratio": "P/FCF", "Last Close Price":"Precio", "Market Capitalization": "Marketcap"
    }

    # CONSULTAR TODAS LAS URLS SIMULTÁNEAMENTE
    urls = urls_y + urls_q

    with ThreadPoolExecutor(max_workers=6) as executor:
        respuestas = list(executor.map(
            lambda url: requests.get(url, headers=headers),
            urls
        ))

    respuestas_y = respuestas[:3]
    respuestas_q = respuestas[3:]

    def procesar_datos(respuestas, nombre_periodo):
        # BUSCAR DATOS EN LAS 3 URLS
        datos = []
        datos_encontrados = set()
        for respuesta in respuestas:
            tablas = pd.read_html(StringIO(respuesta.text))
            for tabla in tablas:
                filas = tabla[tabla.iloc[:, 0].isin(datos_buscar)]
                if not filas.empty:
                    filas = filas[~filas.iloc[:, 0].isin(datos_encontrados)]
                    if not filas.empty:
                        datos.append(filas)
                        datos_encontrados.update(filas.iloc[:, 0])

        # CONVERTIR A DATAFRAME
        datos = pd.concat(datos, ignore_index=True)

        # ELIMINAR TTM
        if "TTM" in datos.columns.get_level_values(0):
            datos = datos.drop(columns=["TTM"], level=0)

        # CONVERTIR ENCABEZADOS EN UNA FILA DE DATOS
        datos.loc[-1] = datos.columns.get_level_values(0).tolist()
        datos.index = datos.index + 1
        datos = datos.sort_index()

        # QUITAR SEGUNDO NIVEL DEL ENCABEZADO
        datos.columns = datos.columns.get_level_values(0)

        # ELIMINAR LOS ENCABEZADOS ORIGINALES
        datos.columns = range(datos.shape[1])

        # TRANSPONER DATAFRAME
        datos = datos.T
        datos.columns = datos.iloc[0]
        datos = datos.iloc[1:]
        datos = datos.reset_index()
        datos = datos.rename(columns={"index": nombre_periodo})

        # ELIMINAR FISCAL YEAR DUPLICADO
        datos = datos.iloc[:, 1:]

        # CAMBIAR NOMBRES
        datos = datos.rename(columns=nombres_columnas)

        # CAMBIAR CURRENT POR ACTUAL
        datos[nombre_periodo] = datos[nombre_periodo].replace("Current","Actual")

        # CONVERTIR "-" A NONE
        datos = datos.replace("-",0)
        datos = datos.fillna(0)

        # PASAR CAPEX A NUMERO POSITIVO
        datos["CapEx"] = pd.to_numeric(datos["CapEx"]).abs()

        # CONVERTIR MÁRGENES A DECIMAL
        columnas_margen = ["Operating Margin", "FCF margin", "ROIC"]
        for columna in columnas_margen:
            datos[columna] = (datos[columna].astype(str).str.replace("%", "", regex=False).astype(float))

        # QUitar comas de marketcap
        datos["Marketcap"] = datos["Marketcap"].astype(str).str.replace(",", "", regex=False)

        # CAMBIAR TIPO
        columnas_int = ["Revenue","FCF","CapEx", "Marketcap"]
        columnas_float = ["Operating Margin","FCF margin","Debt/Equity","Debt/EBITDA","Current ratio",
                          "ROIC","Precio","P/E","P/S","P/B","P/FCF"]
        datos[columnas_int] = datos[columnas_int].astype(int)
        datos[columnas_float] = datos[columnas_float].astype(float)

        # SEPARAR MÉTRICAS Y VALORACIONES
        metricas = datos[[nombre_periodo,"Revenue","FCF","Operating Margin","FCF margin","CapEx",
            "Debt/Equity","Debt/EBITDA","Current ratio","ROIC"]]
        valoraciones = datos[[nombre_periodo,"P/E","P/S","P/B","P/FCF"]]
        mercado = datos[[nombre_periodo,"Precio","Marketcap"]]

        # INVERTIR LISTA
        metricas = metricas.iloc[::-1].reset_index(drop=True)
        valoraciones = valoraciones.iloc[::-1].reset_index(drop=True)
        mercado = mercado.iloc[::-1].reset_index(drop=True)

        metricas = metricas[metricas.iloc[:, 0] != "Actual"].reset_index(drop=True)

        actual = valoraciones[valoraciones.iloc[:, 0] == "Actual"]
        valoraciones = valoraciones[valoraciones.iloc[:, 0] != "Actual"]
        valoraciones = pd.concat([valoraciones,actual],ignore_index=True)

        actual = mercado[mercado.iloc[:, 0] == "Actual"]
        mercado = mercado[mercado.iloc[:, 0] != "Actual"]
        mercado = pd.concat([mercado,actual],ignore_index=True)
        
        return metricas, valoraciones, mercado

    # DATOS ANUALES Y TRIMESTRALES
    metricas_y, valoraciones_y, mercado_y = procesar_datos(respuestas_y, "Fiscal Year")
    metricas_q, valoraciones_q, mercado_q = procesar_datos(respuestas_q, "Fiscal Quarter")
    print(metricas_q)
    return nombre, metricas_y, metricas_q, valoraciones_y, valoraciones_q, mercado_y, mercado_q

def consultar_web2 (ticker):
    url2 = f"https://csimarket.com/stocks/{ticker}-Valuation-Comparisons.html"
    respuesta = requests.get(url2, headers=headers)
    
    if respuesta.status_code != 200:
        return None

    # DATOS QUE QUEREMOS ENCONTRAR
    datos2_buscar = ["Price to earnings PE Ratio","Price to Sales",
        "Price to Free Cash Flow","Price to Book"]
    datos3_buscar= ["Industry", "Sector"]

    # OBTENER LOS DATOS DE LAS TABLAS
    # OBTENER LOS DATOS DE LAS TABLAS
    industrias_v = []
    industria = ""
    sector = ""
    for tabla in pd.read_html(StringIO(respuesta.text)):
        filas = tabla[tabla.iloc[:, 0].astype(str).str.startswith(tuple(datos2_buscar))]
        if not filas.empty:
            filas = pd.concat([tabla.iloc[[0]],filas])
            industrias_v.append(filas)

        filas = tabla[tabla.iloc[:, 0].astype(str).str.startswith(tuple(datos3_buscar))]
        if not filas.empty:
            for fila in filas.iloc[:, 0]:
                if str(fila).startswith("Industry"):
                    industria = str(fila).split("•",1)[-1].strip()
                elif str(fila).startswith("Sector"):
                    sector = str(fila).split("•",1)[-1].strip()

    print("Industria:", industria)
    print("Sector:", sector)

    # CONVERTIR A DATAFRAME
    industrias_v = pd.concat(industrias_v, ignore_index=True)

    # ELIMINAR LOS ENCABEZADOS ORIGINALES
    industrias_v.columns = range(industrias_v.shape[1])

    # TRANSPONER DATAFRAME
    industrias_v = industrias_v.T
    industrias_v.columns = industrias_v.iloc[0]
    industrias_v = industrias_v.iloc[1:]
    industrias_v = industrias_v.reset_index()
    industrias_v = industrias_v.drop(columns=["index"])
    industrias_v = industrias_v[industrias_v.iloc[:, 0] != "Company"].reset_index(drop=True)

    # RENOMBRAR COLUMNAS
    renombrar = {
        "Price to earnings PE Ratio": "P/E",
        "Price to Sales": "P/S",
        "Price to Free Cash Flow": "P/FCF",
        "Price to Book": "P/B"
    }

    for columna in industrias_v.columns:
        for nombre, nuevo_nombre in renombrar.items():
            if str(columna).startswith(nombre):
                industrias_v = industrias_v.rename(columns={columna: nuevo_nombre})

    return industrias_v


