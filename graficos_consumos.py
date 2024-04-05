from sqlalchemy import func
from db import session
from datetime import datetime
from modelos  import DatosMedidorConsumo
import matplotlib.pyplot as plt

def obtener_consumo_por_medidor_y_fecha(fecha, medidor_id):

    # Realizar la consulta a la base de datos para obtener los datos de consumo
    consulta = session.query(
        func.HOUR(DatosMedidorConsumo.time).label('hora'),
        func.MINUTE(DatosMedidorConsumo.time).label('minuto'),
        func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
    ).filter(
        DatosMedidorConsumo.date == fecha,
        DatosMedidorConsumo.meter_id == medidor_id
    ).group_by(
         func.HOUR(DatosMedidorConsumo.time),
         func.MINUTE(DatosMedidorConsumo.time) / 15
    ).order_by( 
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time)
    )
    
    # ejecutar la consulta y obtener los resultados
    resultados = consulta.all()

    # Transformar los resultados en una lista de tuplas de la forma (hora, minuto, consumo_total)
    datos_consumo = [(resultado.hora, resultado.minuto, resultado.consumo_total) for resultado in resultados]

    return datos_consumo

def generar_grafico_consumo_por_horas_dias(fechas, medidor_id):
    # Crear el gráfico
    plt.figure(figsize=(10, 6))

    # Iterar sobre cada fecha
    for fecha in fechas:
        # Obtener los datos de consumo para la fecha y el medidor especificados
        datos_consumo = obtener_consumo_por_medidor_y_fecha(fecha, medidor_id)
        
        # Desempaquetar los datos
        horas = [f"{hora:02d}:{minuto:02d}" for hora, minuto, _ in datos_consumo]
        consumos = [consumo for _, _, consumo in datos_consumo]

        # Encontrar el índice del consumo máximo
        # indice_pico_maximo = consumos.index(max(consumos))
        # hora_pico_maximo = horas[indice_pico_maximo]
        # Verificar si consumos_filtrados no está vacía antes de calcular el máximo
         # Filtrar los valores None de la lista consumos
        consumos_filtrados = [valor for valor in consumos if valor is not None]

        if consumos_filtrados:
            indice_pico_maximo = consumos.index(max(consumos_filtrados))
            hora_pico_maximo = horas[indice_pico_maximo]
            max_consumo = max(consumos_filtrados)
        else:
            # En caso de que todos los valores sean None, se imprime un mensaje apropiado
            print("No hay datos de consumo disponibles para la fecha:", fecha.date())
            continue

        # Graficar los datos de consumo para esta fecha
        plt.plot(horas, consumos, label=f'Fecha: {fecha.date()} - Máx. Demanda: {hora_pico_maximo} - {max_consumo:.8f} kWh')

    # Añadir etiquetas y leyenda al gráfico
    plt.title('Consumo de energía por hora')
    plt.xlabel('Hora del día')
    plt.ylabel('Consumo de energía (kWh)')
    plt.xticks(range(0, len(horas), 4), rotation='vertical')
    plt.legend()
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

# Ejemplo de uso
# fechas = [datetime(2024, 2, 24), datetime(2024, 2, 25),datetime(2024, 2, 26), datetime(2024, 2, 27), datetime(2024, 2, 28), datetime(2024, 2, 29), datetime(2024, 3, 1)]
# medidor_id = "8096"
# generar_grafico_consumo_por_horas_dias(fechas, medidor_id)