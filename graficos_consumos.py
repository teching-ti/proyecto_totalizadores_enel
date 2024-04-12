from sqlalchemy import func, and_
from datetime import time
from db import SessionLocal
from datetime import datetime
from modelos  import DatosMedidorConsumo, Medidores, DatosMedidorInstrumentacion
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np

def grafico_perfiles_instrumentacion(medidores, fecha_inicio, fecha_fin):
    # print(f"Desde Graficos concumos se imprime: {medidores} y las fechas: desde {fecha_inicio} hasta {fecha_fin}")
    # instancia de sesión a la base de datos
    db = SessionLocal()
    # medidores es una lista que posee el id de todos los medidores que se encontraban en el treeview dentro de la pestaña de reportes
    # evaluando cada medidor en la lista
    for medidor_id in medidores:
        # se la consulta para obtener los datos específicos del medidor en el rango de fechas dado
        registros = db.query(
            DatosMedidorInstrumentacion.meter_id,
            DatosMedidorInstrumentacion.date,
            DatosMedidorInstrumentacion.time,
            DatosMedidorInstrumentacion.average_phase_a_current,
            DatosMedidorInstrumentacion.average_phase_b_current,
            DatosMedidorInstrumentacion.average_phase_c_current,
            Medidores.factor
        ).join(
            Medidores, DatosMedidorInstrumentacion.meter_id == Medidores.id
        ).filter(
            and_(
                DatosMedidorInstrumentacion.meter_id == medidor_id,
                DatosMedidorInstrumentacion.date >= fecha_inicio,
                DatosMedidorInstrumentacion.date <= fecha_fin
            )
        ).all()

        # primer valor de la respuesta obtenida del medidor que esta siendo evaluado
        primer_registro = registros[0]
        factor_medidor = primer_registro.factor
        # si coincide con que es las 00:00 horas del primer día seleccionado, se elimina el primer registro de la lista
        if primer_registro.date == fecha_inicio and primer_registro.time == time(0, 0):
            registros = registros[1:]
        
        # selecciona al último dato de las fechas
        ultimo_dia = registros[-1].date
        
        # retirando todos los datos del útimo día excepto las 00.00 horas
        # se modifica la lista de registros
        registros = [registro for registro in registros if registro.date != ultimo_dia or registro.time == time(0, 0)]

        # Procesar datos para obtener promedios y factores
        datos_procesados = {}
        for registro in registros:
            fecha = registro[1]
            hora = registro[2]
            corrientes = [registro[3], registro[4], registro[5]]
            corrientes = [c for c in corrientes if c is not None and c != 'NULL']
            promedio_corrientes = sum(corrientes) / len(corrientes)
            factor = float(registro[6])

            # Calcular el promedio del factor después de asegurarse de que las corrientes no sean None ni 'NULL'
            promedio_factor = float(promedio_corrientes) * factor
            
            print(promedio_factor)
            # Agregar los datos procesados al diccionario
            if fecha not in datos_procesados:
                datos_procesados[fecha] = []
            datos_procesados[fecha].append((hora.hour * 60 + hora.minute, promedio_factor))
            
        # Imprimir el contenido del diccionario
        print("Contenido del diccionario datos_procesados:")
        for fecha, datos in datos_procesados.items():
            print(f"Fecha: {fecha}, Datos: {datos}")





# def obtener_consumo_por_medidor_y_fecha(fecha, medidor_id):
#     db = SessionLocal()
#     Realizar la consulta a la base de datos para obtener los datos de consumo
#     consulta = db.query(
#         func.HOUR(DatosMedidorConsumo.time).label('hora'),
#         func.MINUTE(DatosMedidorConsumo.time).label('minuto'),
#         func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
#     ).filter(
#         DatosMedidorConsumo.date == fecha,
#         DatosMedidorConsumo.meter_id == medidor_id
#     ).group_by(
#          func.HOUR(DatosMedidorConsumo.time),
#          func.MINUTE(DatosMedidorConsumo.time) / 15
#     ).order_by( 
#         func.HOUR(DatosMedidorConsumo.time),
#         func.MINUTE(DatosMedidorConsumo.time)
#     )
    
#     ejecutar la consulta y obtener los resultados
#     resultados = consulta.all()

#     Transformar los resultados en una lista de tuplas de la forma (hora, minuto, consumo_total)
#     datos_consumo = [(resultado.hora, resultado.minuto, resultado.consumo_total) for resultado in resultados]

#     return datos_consumo

# def generar_grafico_consumo_por_horas_dias(fechas, medidor_id):
#     Crear el gráfico
#     plt.figure(figsize=(10, 6))

#     Iterar sobre cada fecha
#     for fecha in fechas:
#         Obtener los datos de consumo para la fecha y el medidor especificados
#         datos_consumo = obtener_consumo_por_medidor_y_fecha(fecha, medidor_id)
        
#         Desempaquetar los datos
#         horas = [f"{hora:02d}:{minuto:02d}" for hora, minuto, _ in datos_consumo]
#         consumos = [consumo for _, _, consumo in datos_consumo]
        
#         print(datos_consumo)
#         Encontrar el índice del consumo máximo
#         indice_pico_maximo = consumos.index(max(consumos))
#         hora_pico_maximo = horas[indice_pico_maximo]
#         Verificar si consumos_filtrados no está vacía antes de calcular el máximo
#         Filtrar los valores None de la lista consumos
#         consumos_filtrados = [valor for valor in consumos if valor is not None]

#         if consumos_filtrados:
#             indice_pico_maximo = consumos.index(max(consumos_filtrados))
#             hora_pico_maximo = horas[indice_pico_maximo]
#             max_consumo = max(consumos_filtrados)
#         else:
#             En caso de que todos los valores sean None, se imprime un mensaje apropiado
#             print("No hay datos de consumo disponibles para la fecha:", fecha.date())
#             continue

#         Graficar los datos de consumo para esta fecha
#         plt.plot(horas, consumos, label=f'Fecha: {fecha.date()} - Máx. Demanda: {hora_pico_maximo} - {max_consumo:.8f} kWh')

#     Añadir etiquetas y leyenda al gráfico
#     plt.title('Consumo de energía por hora')
#     plt.xlabel('Hora del día')
#     plt.ylabel('Consumo de energía (kWh)')
#     plt.xticks(range(0, len(horas), 4), rotation='vertical')
#     plt.legend()
#     plt.grid(axis='y')
#     plt.tight_layout()
#     plt.show()

# # Ejemplo de uso
# fechas = [datetime(2024, 2, 24), datetime(2024, 2, 25),datetime(2024, 2, 26), datetime(2024, 2, 27), datetime(2024, 2, 28), datetime(2024, 2, 29), datetime(2024, 3, 1)]
# medidor_id = "8096"
# generar_grafico_consumo_por_horas_dias(fechas, medidor_id)
