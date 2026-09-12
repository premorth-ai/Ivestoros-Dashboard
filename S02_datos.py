import pandas as pd
import requests
from io import StringIO
import mysql.connector


industrias = [
    {"industria": "Semiconductores", "pe_5ya": 26.5, "pe_actual": 28.5, "ps_5ya": 4.8, "ps_actual": 5.2, "pb_5ya": 6.2, "pb_actual": 6.8, "pfcf_5ya": 25.0, "pfcf_actual": 27.0},
    {"industria": "Software", "pe_5ya": 27.0, "pe_actual": 29.0, "ps_5ya": 5.5, "ps_actual": 6.0, "pb_5ya": 7.5, "pb_actual": 8.0, "pfcf_5ya": 28.5, "pfcf_actual": 30.0},
    {"industria": "Hardware", "pe_5ya": 20.5, "pe_actual": 22.0, "ps_5ya": 2.1, "ps_actual": 2.3, "pb_5ya": 4.5, "pb_actual": 4.8, "pfcf_5ya": 18.5, "pfcf_actual": 19.5},
    {"industria": "Ciberseguridad", "pe_5ya": 32.0, "pe_actual": 34.0, "ps_5ya": 7.2, "ps_actual": 7.8, "pb_5ya": 8.0, "pb_actual": 8.5, "pfcf_5ya": 32.0, "pfcf_actual": 33.5},
    {"industria": "Computación en la nube", "pe_5ya": 30.0, "pe_actual": 32.0, "ps_5ya": 6.0, "ps_actual": 6.5, "pb_5ya": 7.0, "pb_actual": 7.5, "pfcf_5ya": 30.0, "pfcf_actual": 31.0},
    {"industria": "Inteligencia artificial", "pe_5ya": 35.0, "pe_actual": 38.0, "ps_5ya": 8.5, "ps_actual": 9.2, "pb_5ya": 9.5, "pb_actual": 10.2, "pfcf_5ya": 36.0, "pfcf_actual": 38.0},
    {"industria": "Servicios de TI y Consultoría", "pe_5ya": 22.0, "pe_actual": 21.0, "ps_5ya": 2.3, "ps_actual": 2.2, "pb_5ya": 5.0, "pb_actual": 4.8, "pfcf_5ya": 19.0, "pfcf_actual": 18.5},
    {"industria": "Bancos", "pe_5ya": 10.5, "pe_actual": 11.5, "ps_5ya": 1.8, "ps_actual": 1.9, "pb_5ya": 1.1, "pb_actual": 1.2, "pfcf_5ya": 11.0, "pfcf_actual": 11.8},
    {"industria": "Seguros", "pe_5ya": 12.0, "pe_actual": 12.5, "ps_5ya": 2.2, "ps_actual": 2.3, "pb_5ya": 1.4, "pb_actual": 1.5, "pfcf_5ya": 12.5, "pfcf_actual": 13.0},
    {"industria": "Gestión de activos", "pe_5ya": 13.5, "pe_actual": 14.0, "ps_5ya": 2.8, "ps_actual": 2.9, "pb_5ya": 2.1, "pb_actual": 2.2, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Servicios financieros", "pe_5ya": 14.0, "pe_actual": 14.5, "ps_5ya": 2.5, "ps_actual": 2.6, "pb_5ya": 1.8, "pb_actual": 1.9, "pfcf_5ya": 16.0, "pfcf_actual": 16.5},
    {"industria": "Fintech", "pe_5ya": 22.0, "pe_actual": 23.5, "ps_5ya": 4.5, "ps_actual": 4.8, "pb_5ya": 3.8, "pb_actual": 4.0, "pfcf_5ya": 26.0, "pfcf_actual": 27.0},
    {"industria": "Bancos Regionales", "pe_5ya": 9.5, "pe_actual": 10.0, "ps_5ya": 1.5, "ps_actual": 1.6, "pb_5ya": 0.9, "pb_actual": 0.95, "pfcf_5ya": 10.0, "pfcf_actual": 10.5},
    {"industria": "Banca de Inversión y Corretaje", "pe_5ya": 12.5, "pe_actual": 13.0, "ps_5ya": 2.1, "ps_actual": 2.2, "pb_5ya": 1.3, "pb_actual": 1.4, "pfcf_5ya": 13.0, "pfcf_actual": 13.5},
    {"industria": "Farmacéuticas", "pe_5ya": 16.5, "pe_actual": 17.0, "ps_5ya": 3.8, "ps_actual": 3.9, "pb_5ya": 3.2, "pb_actual": 3.3, "pfcf_5ya": 18.0, "pfcf_actual": 18.5},
    {"industria": "Biotecnología", "pe_5ya": 24.0, "pe_actual": 25.0, "ps_5ya": 5.0, "ps_actual": 5.2, "pb_5ya": 4.0, "pb_actual": 4.2, "pfcf_5ya": 25.0, "pfcf_actual": 25.5},
    {"industria": "Equipos médicos", "pe_5ya": 25.0, "pe_actual": 26.0, "ps_5ya": 4.2, "ps_actual": 4.4, "pb_5ya": 4.5, "pb_actual": 4.7, "pfcf_5ya": 26.0, "pfcf_actual": 26.5},
    {"industria": "Servicios hospitalarios", "pe_5ya": 17.5, "pe_actual": 18.0, "ps_5ya": 1.5, "ps_actual": 1.6, "pb_5ya": 2.8, "pb_actual": 2.9, "pfcf_5ya": 16.0, "pfcf_actual": 16.5},
    {"industria": "Diagnóstico", "pe_5ya": 19.0, "pe_actual": 19.5, "ps_5ya": 2.2, "ps_actual": 2.3, "pb_5ya": 3.0, "pb_actual": 3.1, "pfcf_5ya": 20.0, "pfcf_actual": 20.5},
    {"industria": "Gestión de Salud (Managed Care / EPS)", "pe_5ya": 15.0, "pe_actual": 15.5, "ps_5ya": 0.6, "ps_actual": 0.65, "pb_5ya": 2.5, "pb_actual": 2.6, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Petróleo y gas", "pe_5ya": 9.5, "pe_actual": 10.5, "ps_5ya": 1.1, "ps_actual": 1.2, "pb_5ya": 1.3, "pb_actual": 1.4, "pfcf_5ya": 8.0, "pfcf_actual": 8.5},
    {"industria": "Energías renovables", "pe_5ya": 21.0, "pe_actual": 19.5, "ps_5ya": 2.5, "ps_actual": 2.3, "pb_5ya": 2.0, "pb_actual": 1.9, "pfcf_5ya": 20.0, "pfcf_actual": 18.5},
    {"industria": "Servicios petroleros", "pe_5ya": 12.0, "pe_actual": 12.5, "ps_5ya": 1.4, "ps_actual": 1.5, "pb_5ya": 1.6, "pb_actual": 1.7, "pfcf_5ya": 11.0, "pfcf_actual": 11.5},
    {"industria": "Infraestructura de Hidrocarburos", "pe_5ya": 13.0, "pe_actual": 13.5, "ps_5ya": 1.8, "ps_actual": 1.9, "pb_5ya": 1.7, "pb_actual": 1.8, "pfcf_5ya": 13.0, "pfcf_actual": 13.5},
    {"industria": "Maquinaria industrial", "pe_5ya": 18.0, "pe_actual": 19.0, "ps_5ya": 1.5, "ps_actual": 1.6, "pb_5ya": 3.2, "pb_actual": 3.3, "pfcf_5ya": 18.0, "pfcf_actual": 18.5},
    {"industria": "Aeroespacial y defensa", "pe_5ya": 21.5, "pe_actual": 23.0, "ps_5ya": 1.8, "ps_actual": 1.9, "pb_5ya": 4.0, "pb_actual": 4.2, "pfcf_5ya": 17.5, "pfcf_actual": 18.5},
    {"industria": "Construcción", "pe_5ya": 15.5, "pe_actual": 16.0, "ps_5ya": 1.0, "ps_actual": 1.1, "pb_5ya": 2.5, "pb_actual": 2.6, "pfcf_5ya": 20.0, "pfcf_actual": 20.5},
    {"industria": "Transporte", "pe_5ya": 16.5, "pe_actual": 17.0, "ps_5ya": 1.2, "ps_actual": 1.25, "pb_5ya": 3.0, "pb_actual": 3.1, "pfcf_5ya": 14.0, "pfcf_actual": 14.5},
    {"industria": "Ingeniería", "pe_5ya": 16.0, "pe_actual": 16.5, "ps_5ya": 1.1, "ps_actual": 1.15, "pb_5ya": 2.2, "pb_actual": 2.3, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Aerolíneas y Carga Aérea", "pe_5ya": 9.0, "pe_actual": 9.5, "ps_5ya": 0.5, "ps_actual": 0.55, "pb_5ya": 1.6, "pb_actual": 1.65, "pfcf_5ya": 15.0, "pfcf_actual": 14.5},
    {"industria": "Logística y Cadena de Suministro", "pe_5ya": 18.5, "pe_actual": 19.0, "ps_5ya": 0.8, "ps_actual": 0.85, "pb_5ya": 3.5, "pb_actual": 3.6, "pfcf_5ya": 10.0, "pfcf_actual": 10.5},
    {"industria": "Automóviles", "pe_5ya": 8.5, "pe_actual": 9.0, "ps_5ya": 0.6, "ps_actual": 0.65, "pb_5ya": 1.8, "pb_actual": 1.85, "pfcf_5ya": 10.5, "pfcf_actual": 11.0},
    {"industria": "Retail", "pe_5ya": 19.0, "pe_actual": 19.5, "ps_5ya": 1.2, "ps_actual": 1.25, "pb_5ya": 3.5, "pb_actual": 3.6, "pfcf_5ya": 16.0, "pfcf_actual": 16.5},
    {"industria": "Hoteles y restaurantes", "pe_5ya": 21.0, "pe_actual": 21.5, "ps_5ya": 2.0, "ps_actual": 2.1, "pb_5ya": 4.2, "pb_actual": 4.3, "pfcf_5ya": 20.0, "pfcf_actual": 20.5},
    {"industria": "Lujo", "pe_5ya": 23.5, "pe_actual": 22.0, "ps_5ya": 3.2, "ps_actual": 3.0, "pb_5ya": 6.0, "pb_actual": 5.8, "pfcf_5ya": 24.0, "pfcf_actual": 22.5},
    {"industria": "Entretenimiento", "pe_5ya": 20.0, "pe_actual": 20.5, "ps_5ya": 1.4, "ps_actual": 1.45, "pb_5ya": 2.8, "pb_actual": 2.9, "pfcf_5ya": 19.0, "pfcf_actual": 19.5},
    {"industria": "E-Commerce / Comercio Electrónico", "pe_5ya": 27.0, "pe_actual": 28.5, "ps_5ya": 2.2, "ps_actual": 2.3, "pb_5ya": 4.8, "pb_actual": 5.0, "pfcf_5ya": 28.0, "pfcf_actual": 29.0},
    {"industria": "Indumentaria y Calzado", "pe_5ya": 17.5, "pe_actual": 18.0, "ps_5ya": 1.4, "ps_actual": 1.45, "pb_5ya": 3.2, "pb_actual": 3.3, "pfcf_5ya": 17.0, "pfcf_actual": 17.5},
    {"industria": "Bebidas", "pe_5ya": 19.5, "pe_actual": 20.0, "ps_5ya": 2.1, "ps_actual": 2.15, "pb_5ya": 4.8, "pb_actual": 4.9, "pfcf_5ya": 22.0, "pfcf_actual": 22.5},
    {"industria": "Alimentos", "pe_5ya": 18.5, "pe_actual": 19.0, "ps_5ya": 1.5, "ps_actual": 1.55, "pb_5ya": 3.5, "pb_actual": 3.6, "pfcf_5ya": 19.0, "pfcf_actual": 19.5},
    {"industria": "Productos del hogar", "pe_5ya": 20.0, "pe_actual": 20.5, "ps_5ya": 2.0, "ps_actual": 2.05, "pb_5ya": 4.0, "pb_actual": 4.1, "pfcf_5ya": 21.0, "pfcf_actual": 21.5},
    {"industria": "Higiene personal", "pe_5ya": 20.5, "pe_actual": 21.0, "ps_5ya": 2.2, "ps_actual": 2.25, "pb_5ya": 4.5, "pb_actual": 4.6, "pfcf_5ya": 21.0, "pfcf_actual": 21.5},
    {"industria": "Tabaco", "pe_5ya": 10.0, "pe_actual": 10.5, "ps_5ya": 1.8, "ps_actual": 1.85, "pb_5ya": 3.0, "pb_actual": 3.1, "pfcf_5ya": 11.0, "pfcf_actual": 11.5},
    {"industria": "Supermercados e Hipermercados", "pe_5ya": 14.5, "pe_actual": 15.0, "ps_5ya": 0.4, "ps_actual": 0.42, "pb_5ya": 2.2, "pb_actual": 2.3, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Telecomunicaciones", "pe_5ya": 11.5, "pe_actual": 12.0, "ps_5ya": 1.6, "ps_actual": 1.65, "pb_5ya": 1.4, "pb_actual": 1.45, "pfcf_5ya": 12.0, "pfcf_actual": 12.5},
    {"industria": "Redes sociales", "pe_5ya": 22.0, "pe_actual": 23.5, "ps_5ya": 4.0, "ps_actual": 4.2, "pb_5ya": 4.5, "pb_actual": 4.7, "pfcf_5ya": 24.0, "pfcf_actual": 25.0},
    {"industria": "Medios", "pe_5ya": 15.0, "pe_actual": 15.5, "ps_5ya": 1.5, "ps_actual": 1.55, "pb_5ya": 2.0, "pb_actual": 2.1, "pfcf_5ya": 14.0, "pfcf_actual": 14.5},
    {"industria": "Entretenimiento digital", "pe_5ya": 23.0, "pe_actual": 24.0, "ps_5ya": 2.8, "ps_actual": 2.9, "pb_5ya": 3.8, "pb_actual": 3.9, "pfcf_5ya": 21.0, "pfcf_actual": 21.5},
    {"industria": "Videojuegos y Software Interactivo", "pe_5ya": 24.5, "pe_actual": 25.0, "ps_5ya": 4.2, "ps_actual": 4.3, "pb_5ya": 3.5, "pb_actual": 3.6, "pfcf_5ya": 24.0, "pfcf_actual": 24.5},
    {"industria": "REITs residenciales", "pe_5ya": 17.0, "pe_actual": 17.5, "ps_5ya": 4.5, "ps_actual": 4.6, "pb_5ya": 1.5, "pb_actual": 1.55, "pfcf_5ya": 20.0, "pfcf_actual": 20.5},
    {"industria": "REITs comerciales", "pe_5ya": 15.0, "pe_actual": 15.5, "ps_5ya": 3.2, "ps_actual": 3.3, "pb_5ya": 1.2, "pb_actual": 1.25, "pfcf_5ya": 16.0, "pfcf_actual": 16.5},
    {"industria": "Centros de datos", "pe_5ya": 24.0, "pe_actual": 25.5, "ps_5ya": 6.5, "ps_actual": 6.8, "pb_5ya": 2.2, "pb_actual": 2.3, "pfcf_5ya": 25.0, "pfcf_actual": 26.0},
    {"industria": "Infraestructura inmobiliaria", "pe_5ya": 18.0, "pe_actual": 18.5, "ps_5ya": 4.0, "ps_actual": 4.1, "pb_5ya": 1.6, "pb_actual": 1.65, "pfcf_5ya": 22.0, "pfcf_actual": 22.5},
    {"industria": "REITs Industriales y Logística", "pe_5ya": 21.0, "pe_actual": 21.5, "ps_5ya": 7.0, "ps_actual": 7.2, "pb_5ya": 2.0, "pb_actual": 2.05, "pfcf_5ya": 23.0, "pfcf_actual": 23.5},
    {"industria": "REITs de Salud e Instalaciones Médicas", "pe_5ya": 16.5, "pe_actual": 17.0, "ps_5ya": 5.2, "ps_actual": 5.3, "pb_5ya": 1.4, "pb_actual": 1.45, "pfcf_5ya": 17.0, "pfcf_actual": 17.5},
    {"industria": "Minería", "pe_5ya": 12.5, "pe_actual": 13.0, "ps_5ya": 1.2, "ps_actual": 1.25, "pb_5ya": 1.5, "pb_actual": 1.55, "pfcf_5ya": 11.0, "pfcf_actual": 11.5},
    {"industria": "Químicos", "pe_5ya": 15.0, "pe_actual": 15.5, "ps_5ya": 1.6, "ps_actual": 1.65, "pb_5ya": 2.2, "pb_actual": 2.25, "pfcf_5ya": 16.0, "pfcf_actual": 16.5},
    {"industria": "Metales", "pe_5ya": 12.0, "pe_actual": 12.5, "ps_5ya": 1.0, "ps_actual": 1.05, "pb_5ya": 1.3, "pb_actual": 1.35, "pfcf_5ya": 10.0, "pfcf_actual": 10.5},
    {"industria": "Materiales de construcción", "pe_5ya": 16.5, "pe_actual": 17.0, "ps_5ya": 1.5, "ps_actual": 1.55, "pb_5ya": 2.0, "pb_actual": 2.05, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Empaques y Embalajes", "pe_5ya": 15.5, "pe_actual": 16.0, "ps_5ya": 1.1, "ps_actual": 1.15, "pb_5ya": 2.4, "pb_actual": 2.45, "pfcf_5ya": 14.0, "pfcf_actual": 14.5},
    {"industria": "Electricidad", "pe_5ya": 17.0, "pe_actual": 17.5, "ps_5ya": 1.8, "ps_actual": 1.85, "pb_5ya": 1.8, "pb_actual": 1.85, "pfcf_5ya": 17.0, "pfcf_actual": 17.5},
    {"industria": "Agua", "pe_5ya": 20.0, "pe_actual": 20.5, "ps_5ya": 2.2, "ps_actual": 2.25, "pb_5ya": 2.1, "pb_actual": 2.15, "pfcf_5ya": 23.0, "pfcf_actual": 23.5},
    {"industria": "Gas", "pe_5ya": 16.0, "pe_actual": 16.5, "ps_5ya": 1.6, "ps_actual": 1.65, "pb_5ya": 1.6, "pb_actual": 1.65, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Infraestructura energética", "pe_5ya": 15.5, "pe_actual": 16.0, "ps_5ya": 1.5, "ps_actual": 1.55, "pb_5ya": 1.5, "pb_actual": 1.55, "pfcf_5ya": 15.0, "pfcf_actual": 15.5},
    {"industria": "Productores Independientes de Energía", "pe_5ya": 14.0, "pe_actual": 14.5, "ps_5ya": 1.3, "ps_actual": 1.35, "pb_5ya": 1.4, "pb_actual": 1.45, "pfcf_5ya": 13.0, "pfcf_actual": 13.5}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}

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