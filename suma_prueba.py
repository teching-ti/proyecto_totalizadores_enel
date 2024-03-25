from db import SessionLocal, session
from sqlalchemy import create_engine, func
from modelos import DatosMedidorConsumo
import pandas as pd

import matplotlib.pyplot as plt

def obtener_suma_kwh_del(fecha_inicio, fecha_fin, meter_id):

    # realizar la consulta y aplicar la función de agregación
    suma_kwh_del = session.query(func.sum(DatosMedidorConsumo.kwh_del)).\
                    filter(DatosMedidorConsumo.meter_id == meter_id).\
                    filter(DatosMedidorConsumo.date >= fecha_inicio).\
                    filter(DatosMedidorConsumo.date <= fecha_fin).scalar()

    return suma_kwh_del

def obtener_consumo_por_dia(fecha_inicio, fecha_fin, meter_id):
    # realizar la consulta y aplicar la función de agregación para sumar el consumo de kwh_del por día
    resultado = session.query(
        DatosMedidorConsumo.date,
        func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
    ).filter(
        DatosMedidorConsumo.meter_id == meter_id,
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin
    ).group_by(
        DatosMedidorConsumo.date
    ).all()

    return resultado

def obtener_hora_maxima_demanda(fecha_inicio, fecha_fin, meter_id):
    # Realizar la consulta y aplicar la función de agregación para sumar el consumo de kwh_del por hora
    resultado = session.query(
        DatosMedidorConsumo.date,
        DatosMedidorConsumo.time,
        func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
    ).filter(
        DatosMedidorConsumo.meter_id == meter_id,
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin
    ).group_by(
        DatosMedidorConsumo.date,
        DatosMedidorConsumo.time
    ).order_by(
        func.sum(DatosMedidorConsumo.kwh_del).desc()
    ).first()

    return resultado
'''
# esta funcion va de la mano con la de generar grafico
def obtener_consumo_diario(fecha):
    # Consultar la base de datos para obtener los registros de consumo de energía para la fecha seleccionada
    registros = session.query(DatosMedidorConsumo).\
                    filter(DatosMedidorConsumo.date == fecha).all()

    # Crear una lista de tuplas con la hora y el consumo de energía para cada registro
    datos_dia = [(f"{registro.time.hour:02}:{registro.time.minute:02}", registro.kwh_del) for registro in registros]
    
    return datos_dia

# esta funcion va de la mano con la de obtener_consumo_diario
def generar_grafico_consumo_diario(datos_dia):
    import matplotlib.pyplot as plt

    # Crear un DataFrame a partir de los datos
    df = pd.DataFrame(datos_dia, columns=['Hora', 'Consumo'])

    df = df.groupby('Hora').sum().reset_index()

    # Encontrar el índice del pico máximo de consumo
    indice_pico_maximo = df['Consumo'].idxmax()

    # Obtener la hora del pico máximo
    hora_pico_maximo = df.loc[indice_pico_maximo, 'Hora']

    # Seleccionar solo algunas etiquetas de hora para mostrar
    intervalo = 4  # Mostrar una etiqueta cada 3 horas
    etiquetas_hora = [df['Hora'].iloc[i] for i in range(0, len(df), intervalo)]
    if hora_pico_maximo not in etiquetas_hora:
        # Asegurarse de que la hora del pico máximo esté incluida en las etiquetas
        etiquetas_hora.append(hora_pico_maximo)
        etiquetas_hora.sort()

    # Graficar los datos
    plt.figure(figsize=(10, 8))
    plt.plot(df['Hora'], df['Consumo'], color='b', linestyle='-')
    plt.title('Hora de máxima demanda')
    #plt.xlabel('Hora del día')
    plt.ylabel('Consumo de energía (kWh)')
    plt.xticks(etiquetas_hora, rotation='vertical')  # Usar solo algunas etiquetas de hora
    plt.axvline(x=hora_pico_maximo, color='red', linestyle='--', label=f'Pico máximo a las {hora_pico_maximo}')
    #plt.legend()
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()
'''

# fecha_inicio = datetime.datetime(2024, 2, 26).date()
# fecha_fin = datetime.datetime(2024, 3, 4).date()
# # actualmente se devuelve una tupla de tres datos
# print(obtener_suma_kwh_del(fecha_inicio, fecha_fin, '08119'))
    
# ejemplo de uso para generar gráfico de horas por dia (la idea es obtener un promedio o una sumatoria por semana para en base a ello obtener su gráfico)
# Fecha seleccionada para obtener los datos

'''
fecha_seleccionada = '2024-03-03'

# Obtener los datos de consumo para la fecha seleccionada
datos_dia = obtener_consumo_diario(fecha_seleccionada)

# Generar y mostrar el gráfico de consumo diario
generar_grafico_consumo_diario(datos_dia)
'''
