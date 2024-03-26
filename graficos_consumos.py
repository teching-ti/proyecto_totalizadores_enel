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
    
    # Ejecutar la consulta y obtener los resultados
    resultados = consulta.all()
    
    # Transformar los resultados en una lista de tuplas de la forma (hora, minuto, consumo_total)
    datos_consumo = [(resultado.hora, resultado.minuto, resultado.consumo_total) for resultado in resultados]
    
    return datos_consumo

def generar_grafico_consumo_por_horas(fechas, medidor_id):
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
        indice_pico_maximo = consumos.index(max(consumos))
        hora_pico_maximo = horas[indice_pico_maximo]

        # Graficar los datos de consumo para esta fecha
        plt.plot(horas, consumos, label=f'Fecha: {fecha} - Máx. Demanda: {hora_pico_maximo} - {max(consumos):.8f} kWh')

    # Añadir etiquetas y leyenda al gráfico
    plt.title('Consumo de energía por hora')
    plt.xlabel('Hora del día')
    plt.ylabel('Consumo de energía (kWh)')
    plt.xticks(rotation='vertical')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Ejemplo de uso
fechas = [datetime(2024, 2, 24), datetime(2024, 2, 25),datetime(2024, 2, 26), datetime(2024, 2, 27), datetime(2024, 2, 28), datetime(2024, 2, 29), datetime(2024, 3, 1)]
medidor_id = "8096"
generar_grafico_consumo_por_horas(fechas, medidor_id)