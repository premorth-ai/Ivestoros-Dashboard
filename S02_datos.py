import pandas as pd
import requests
from pathlib import Path
from io import StringIO

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}

# Encuentra la ruta exacta del archivo en la misma carpeta
ruta = Path(__file__).parent / "industrias.csv"
# Carga los datos en la variable 'df'
industrias = pd.read_csv(ruta, sep=";", decimal=",")

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
        "PE Ratio": "P/E","PB Ratio": "P/B","P/FCF Ratio": "P/FCF"
    }

    def procesar_datos(urls, nombre_periodo):
        # BUSCAR DATOS EN LAS 3 URLs
        datos = []
        datos_encontrados = set()
        precio_actual = None
        marketcap_actual = None
        for url in urls:
            respuesta = requests.get(url, headers=headers)
            tablas = pd.read_html(StringIO(respuesta.text))
            for tabla in tablas:
                filas = tabla[tabla.iloc[:, 0].isin(datos_buscar)]
                if not filas.empty:
                    if "Current" in tabla.columns.get_level_values(0):
                        for _, fila in filas.iterrows():
                            if fila.iloc[0] == "Last Close Price":
                                precio_actual = fila["Current"].iloc[0]
                            elif fila.iloc[0] == "Market Capitalization":
                                marketcap_actual = fila["Current"].iloc[0]
                    filas = filas[~filas.iloc[:, 0].isin(datos_encontrados)]
                    if not filas.empty:
                        datos.append(filas)
                        datos_encontrados.update(filas.iloc[:, 0])
        # CONVERTIR A DATAFRAME
        datos = pd.concat(datos, ignore_index=True)
        # ELIMINAR TTM Y CURRENT
        if "TTM" in datos.columns.get_level_values(0):
            datos = datos.drop(columns=["TTM"], level=0)
        if "Current" in datos.columns.get_level_values(0):
            datos = datos.drop(columns=["Current"], level=0)
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
        # CONVERTIR "-" A NONE
        datos = datos.replace("-",0)
        datos = datos.fillna(0)
        # PASAR CAPEX A POSITIVO
        # PASAR CAPEX A NUMERO POSITIVO
        datos["CapEx"] = pd.to_numeric(datos["CapEx"]).abs()   
        # CONVERTIR MÁRGENES A DECIMAL
        columnas_margen = ["Operating Margin", "FCF margin", "ROIC"]
        for columna in columnas_margen:
            datos[columna] = (datos[columna].astype(str).str.replace("%", "", regex=False).astype(float)/ 100)
        return datos, precio_actual, marketcap_actual

    # DATOS ANUALES Y TRIMESTRALES
    datos_y, precio_actual, marketcap_actual = procesar_datos(urls_y, "Fiscal Year")
    datos_q, _, _ = procesar_datos(urls_q, "Fiscal Quarter")
    return nombre, datos_y, datos_q, precio_actual, marketcap_actual

# RENOMBRAR
def no_sql_renombrar(datos_y,datos_q,precio_actual,marketcap_actual):
    datos_y = datos_y.rename(columns={
        "Fiscal Year": "fiscal_year",
        "Revenue": "revenue",
        "FCF": "fcf",
        "Operating Margin": "operating_margin",
        "FCF margin": "fcf_margin",
        "CapEx": "capex",
        "P/E": "pe",
        "P/S": "ps",
        "P/B": "pb",
        "P/FCF": "p_fcf",
        "Debt/Equity": "debt_equity",
        "Debt/EBITDA": "debt_ebitda",
        "Current ratio": "current_ratio",
        "ROIC": "roic",
        "Last Close Price": "precio",
        "Market Capitalization": "marketcap"
    })
    datos_q = datos_q.rename(columns={
        "Fiscal Quarter": "fiscal_quarter",
        "Revenue": "revenue",
        "FCF": "fcf",
        "Operating Margin": "operating_margin",
        "FCF margin": "fcf_margin",
        "CapEx": "capex",
        "P/E": "pe",
        "P/S": "ps",
        "P/B": "pb",
        "P/FCF": "p_fcf",
        "Debt/Equity": "debt_equity",
        "Debt/EBITDA": "debt_ebitda",
        "Current ratio": "current_ratio",
        "ROIC": "roic",
        "Last Close Price": "precio",
        "Market Capitalization": "marketcap"
    })

    return datos_y,datos_q,precio_actual,marketcap_actual

# CAMBIAR TIPO E INVERTIR LISTA
def cambiar_tipo(datos_y,datos_q,precio_actual,marketcap_actual):
    columnas_int = ["revenue","fcf","capex","marketcap"]
    columnas_float = ["operating_margin","fcf_margin","pe","ps","pb","p_fcf","debt_equity","debt_ebitda","current_ratio","roic","precio"]
    datos_y["fiscal_year"] = datos_y["fiscal_year"].astype(str)
    datos_q["fiscal_quarter"] = datos_q["fiscal_quarter"].astype(str)
    datos_y[columnas_int] = datos_y[columnas_int].astype(int)
    datos_q[columnas_int] = datos_q[columnas_int].astype(int)
    datos_y[columnas_float] = datos_y[columnas_float].astype(float)
    datos_q[columnas_float] = datos_q[columnas_float].astype(float)
    datos_y = datos_y.iloc[::-1].reset_index(drop=True)
    datos_q = datos_q.iloc[::-1].reset_index(drop=True)
    precio_actual = float(precio_actual)
    marketcap_actual = int(marketcap_actual)

    return datos_y,datos_q,precio_actual,marketcap_actual