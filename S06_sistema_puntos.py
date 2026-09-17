# Sistema de puntos
def sistema_puntos(metricas_y):
    calificaciones = {}

    rangos = {
    "Revenue": [
        (0.15,10),(0.11,9),(0.08,8),(0.05,7),(0.02,6),
        (0,5),(-0.05,4),(-0.10,3),(-0.20,2)
    ],
    "FCF": [
        (0.25,10),(0.18,9),(0.12,8),(0.07,7),(0.03,6),
        (-0.03,5),(-0.10,4),(-0.20,3),(-0.35,2)
    ],
    "Operating Margin": [
        (0.30,10),(0.20,9),(0.15,8),(0.10,7),(0.07,6),
        (0.05,5),(0.04,4),(0.03,3),(0,2)
    ],
    "ROIC": [
        (0.30,10),(0.20,9),(0.15,8),(0.10,7),(0.07,6),
        (0.05,5),(0.04,4),(0.03,3),(0,2)
    ],
    "FCF margin": [
        (0.225,10),(0.15,9),(0.10,8),(0.07,7),(0.05,6),
        (0.04,5),(0.03,4),(0.02,3),(0,2)
    ],
    "Debt/Equity": [
        (0.2,10),(0.4,9),(0.6,8),(0.8,7),(1.0,6),
        (1.4,5),(1.8,4),(2.2,3),(3.0,2)
    ],
    "Debt/EBITDA": [
        (0.5,10),(1.0,9),(1.5,8),(2.0,7),(2.5,6),
        (3.0,5),(3.5,4),(4.0,3),(5.0,2)
    ],
    "Current ratio": [
        (2.5,10),(2.2,9),(1.9,8),(1.6,7),(1.3,6),
        (1.1,5),(0.9,4),(0.7,3),(0.5,2)
    ]
    }

    menor_es_mejor = {"Debt/Equity","Debt/EBITDA"}

    for metric, rangos_metric in rangos.items():
        datos = metricas_y[metric].dropna()

        if datos.empty:
            calificaciones[metric] = None
            continue

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