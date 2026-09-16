# SISTEMA DE PUNTOS
def sistema_puntos(data):
    evaluaciones = data.attrs.get("evaluaciones",{})
    resultados = {}
    def calcular_puntaje(valor,rangos,direccion="direct"):
        for limite,puntaje,estricto in rangos:
            if direccion == "direct":
                if (valor > limite if estricto else valor >= limite):
                    return puntaje
            else:
                if (valor < limite if estricto else valor <= limite):
                    return puntaje
        return 0

    def calcular_ajuste(evaluacion,peso,direccion="direct",usar_cagr=True):
        ajuste = 0
        for clave in ["promedio","anterior","antiguo"]:
            valor = evaluacion[clave]
            if valor is not None:
                if direccion == "direct":
                    if valor > 5:
                        ajuste += peso
                    elif valor < -5:
                        ajuste -= peso
                else:
                    if valor < -5:
                        ajuste += peso
                    elif valor > 5:
                        ajuste -= peso
        if usar_cagr and evaluacion["cagr"] is not None:
            if direccion == "direct":
                if evaluacion["cagr"] > 0.05:
                    ajuste += peso
                elif evaluacion["cagr"] < -0.05:
                    ajuste -= peso
            else:
                if evaluacion["cagr"] < -0.05:
                    ajuste += peso
                elif evaluacion["cagr"] > 0.05:
                    ajuste -= peso
        ajuste += evaluacion["tendencia"] * peso
        return ajuste
    # REVENUE
    if "Revenue" in evaluaciones:
        evaluacion = evaluaciones["Revenue"]
        cagr = evaluacion["cagr"]
        if cagr is not None:
            rangos = [
                (0.15,9,True),(0.11,8,False),(0.08,7,False),
                (0.05,6,False),(0.02,5,False),(0,4,False),
                (-0.05,3,False),(-0.10,2,False),(-0.20,1,False)
            ]
            puntaje = calcular_puntaje(cagr,rangos)
            ajuste = calcular_ajuste(evaluacion,0.25,usar_cagr=False)
            resultados["Revenue"] = min(max(puntaje + ajuste,0),10)
    # FCF
    if "FCF" in evaluaciones:
        evaluacion = evaluaciones["FCF"]
        cagr = evaluacion["cagr"]
        if cagr is not None:
            rangos = [
                (0.25,9,True),(0.18,8,False),(0.12,7,False),
                (0.07,6,False),(0.03,5,False),(-0.03,4,False),
                (-0.10,3,False),(-0.20,2,False),(-0.35,1,False)
            ]
            puntaje = calcular_puntaje(cagr,rangos)
            ajuste = calcular_ajuste(evaluacion,0.25,usar_cagr=False)
            resultados["FCF"] = min(max(puntaje + ajuste,0),10)
    # OPERATING MARGIN
    if "Operating Margin" in evaluaciones:
        evaluacion = evaluaciones["Operating Margin"]
        reciente = data["Operating Margin"].iloc[-1]
        rangos = [
            (0.30,9,False),(0.20,8,False),(0.15,7,False),
            (0.10,6,False),(0.07,5,False),(0.05,4,False),
            (0.04,3,False),(0.03,2,False),(0,1,True)
        ]
        puntaje = calcular_puntaje(reciente,rangos)
        ajuste = calcular_ajuste(evaluacion,0.2)
        resultados["Operating Margin"] = min(max(puntaje + ajuste,0),10)
    # ROIC
    if "ROIC" in evaluaciones:
        evaluacion = evaluaciones["ROIC"]
        reciente = data["ROIC"].iloc[-1]
        rangos = [
            (0.30,9,False),(0.20,8,False),(0.15,7,False),
            (0.10,6,False),(0.07,5,False),(0.05,4,False),
            (0.04,3,False),(0.03,2,False),(0,1,True)
        ]
        puntaje = calcular_puntaje(reciente,rangos)
        ajuste = calcular_ajuste(evaluacion,0.2)
        resultados["ROIC"] = min(max(puntaje + ajuste,0),10)
    # FCF MARGIN
    if "FCF margin" in evaluaciones:
        evaluacion = evaluaciones["FCF margin"]
        reciente = data["FCF margin"].iloc[-1]
        rangos = [
            (0.225,9,False),(0.15,8,False),(0.10,7,False),
            (0.07,6,False),(0.05,5,False),(0.04,4,False),
            (0.03,3,False),(0.02,2,False),(0,1,True)
        ]
        puntaje = calcular_puntaje(reciente,rangos)
        ajuste = calcular_ajuste(evaluacion,0.2)
        resultados["FCF margin"] = min(max(puntaje + ajuste,0),10)
    # DEBT TO EQUITY
    if "Debt/Equity" in evaluaciones:
        evaluacion = evaluaciones["Debt/Equity"]
        reciente = data["Debt/Equity"].iloc[-1]
        rangos = [
            (0.2,9,True),(0.4,8,False),(0.6,7,False),
            (0.8,6,False),(1.0,5,False),(1.4,4,False),
            (1.8,3,False),(2.2,2,False),(3.0,1,False)
        ]
        puntaje = calcular_puntaje(reciente,rangos,"inverse")
        ajuste = calcular_ajuste(evaluacion,0.2,"inverse")
        resultados["Debt/Equity"] = min(max(puntaje + ajuste,0),10)
    # DEBT TO EBITDA
    if "Debt/EBITDA" in evaluaciones:
        evaluacion = evaluaciones["Debt/EBITDA"]
        reciente = data["Debt/EBITDA"].iloc[-1]
        rangos = [
            (0.5,9,True),(1.0,8,False),(1.5,7,False),
            (2.0,6,False),(2.5,5,False),(3.0,4,False),
            (3.5,3,False),(4.0,2,False),(5.0,1,False)
        ]
        puntaje = calcular_puntaje(reciente,rangos,"inverse")
        ajuste = calcular_ajuste(evaluacion,0.2,"inverse")
        resultados["Debt/EBITDA"] = min(max(puntaje + ajuste,0),10)
    # CURRENT RATIO
    if "Current ratio" in evaluaciones:
        evaluacion = evaluaciones["Current ratio"]
        reciente = data["Current ratio"].iloc[-1]
        rangos = [
            (2.5,9,True),(2.2,8,False),(1.9,7,False),
            (1.6,6,False),(1.3,5,False),(1.1,4,False),
            (0.9,3,False),(0.7,2,False),(0.5,1,False)
        ]
        puntaje = calcular_puntaje(reciente,rangos)
        if reciente > 8.0:
            puntaje = min(puntaje,5)
        elif reciente > 6.0:
            puntaje = min(puntaje,6)
        elif reciente > 4.0:
            puntaje = min(puntaje,7)
        elif reciente > 2.5:
            puntaje = min(puntaje,8)
        ajuste = calcular_ajuste(evaluacion,0.2)
        resultados["Current ratio"] = min(max(puntaje + ajuste,0),10)

    return resultados