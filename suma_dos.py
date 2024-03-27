'''***** NO TOCAR *****'''
''' OBTIENE LA SUMA COMPLETA DE CONSUMOS DE UN MEDIDOR DENTRO DE UN RANGO '''
# en el archivo suma_dos se peude obtener la suma total en base a las horas en un rango de fechas
# de estos datos sale un gráfico, primero es importante que el programa reconozca que fechas son las que tienen datos
# y en base a las fechas y las horas se coloca la información
# este archivo funciona en base a lógica, la interfaz usará la función en este archivo para que reciba datos y trabaje en base a ello.

from sqlalchemy import func
from db import session
from datetime import datetime
from modelos  import DatosMedidorConsumo

def obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id):
    sumatoria_total = []

    # se realiza consulta a la base de datos para obtenr el consumo total por cuarto de hora en el rango de fechas dado y para el medidor especificado
    consulta = session.query(
        func.HOUR(DatosMedidorConsumo.time).label('hora'),
        func.MINUTE(DatosMedidorConsumo.time).label('minuto'),
        func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
    ).filter(
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin,
        DatosMedidorConsumo.meter_id == medidor_id
    ).group_by(
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time) / 15
    ).order_by( 
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time)
    )

    # se ejecuta la consulta
    resultados = consulta.all()
    
    # imrpimiendo los resultados por horas, se pueden colocar las variables que contienen estos datos
    # for resultado in resultados:
    #     hora = resultado.hora
    #     minuto = resultado.minuto
    #     consumo_total = resultado.consumo_total
    #     #print(f"Hora: {hora:02d}:{minuto:02d} = {consumo_total}")
    #     sumatoria_total.append(consumo_total)

    # print(sum(sumatoria_total))
    print(resultados)

# se asignan datos para realizar pruebas
fecha_inicio = datetime(2024, 2, 24)
fecha_fin = datetime(2024, 3, 1)
medidor_id = "8096"

obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)