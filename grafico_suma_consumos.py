'''
ESTE MÓDULO REALIZA UNA SUMA DE CONSUMOS POR HORAS MARCADAS EN UN RANGO DE FECHAS SELECCIONADAS, PARA GENERAR EL GRÁFICO QUE SE ENCUENTRA EN LA HOJA TRES DEL EJEMPLO
'''
from sqlalchemy import func
from db import session
from datetime import datetime
from modelos  import DatosMedidorConsumo
import matplotlib.pyplot as plt
from decimal import Decimal

def obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id):
    sumatoria_total = []
    # se realiza consulta a la base de datos para obtenr el consumo total por cuarto de hora en el rango de fechas dado y para el medidor especificado
    consulta = session.query(
        # aquí se obtienen las horas y minutos, luego se asigna el label para nombrar asi a la columna
        func.HOUR(DatosMedidorConsumo.time).label('hora'),
        func.MINUTE(DatosMedidorConsumo.time).label('minuto'),
        # se usa sum para sumar los valores en la columna, luego se le asigna nombre a la columna
        func.sum(DatosMedidorConsumo.kwh_del).label('consumo_total')
    ).filter(
        # se usa la funcion filter para filtrar los resultados
        # se filtran los datos que solo incluyan las fechas especificadas
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin,
        DatosMedidorConsumo.meter_id == medidor_id
    ).group_by(
        # se agrupan los resultados por cuarto de hora en minutos
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time) / 15
    ).order_by( 
        # se ordenará por hora y luego por minuto
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time)
    )

    # se ejecuta la consulta
    resultados = consulta.all()
    # usamos una comprensión de lista para iterar sobre los reesultados de la consulta anterior, por cada resultado se crea una tupla
    # que contiene la hora, minuto y consumo total, estas tuplas se agregan a una lista llamada 'datos_consumo'
    datos_consumo = [(resultado.hora, resultado.minuto, resultado.consumo_total) for resultado in resultados]
    

    ''' /*********************************/Desde este punto se obtendrán datos para realizar el reporte\*********************************'''
    # se crean las variables para calcular los datos máximos
    max_consumo = float('-inf')
    hora_max_consumo = None

    for resultado in resultados:
        hora = resultado.hora
        minuto = resultado.minuto
        consumo_total = resultado.consumo_total
        # se añade a la lsita sumatoria_total la suma de consumos obtenidos
        sumatoria_total.append(consumo_total)

        # se calcula cual es el valor de maximo consumo para asi obtener la hora y minuto de máximo consumo
        if consumo_total > max_consumo:
            max_consumo = consumo_total
            hora_max_consumo = (hora, minuto)

    # se crea una variable que almacenará la suma de los elementos en la lista
    resultado_total = sum(sumatoria_total)

    # consulta para obtener el numero de dias de los que se tiene registro en el rango de fechas seleccionado
    consulta_numero_dias = session.query(
        # cuenta los días únicos en los que se registraron lecturas
        func.count(func.distinct(DatosMedidorConsumo.date)).label('dias_unicos')
    ).filter(
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin,
        DatosMedidorConsumo.meter_id == medidor_id,
        # siempre y cuando no se obtenga información en el campo requerido
        DatosMedidorConsumo.kwh_del != None
    )

    # se gurda la información obtenida en una variable
    resultado_n_dias = consulta_numero_dias.first()
    # se guarda especificamente el numero de dias ya que el resultado como colunma a mostrar fue 'dias_unicos'
    dias_con_datos = resultado_n_dias.dias_unicos

    # se compara el número de días con los que se tiene registro, esto a fin de obtener un cálculo mensual
    # este ejemplo es para febrero, obtener el mes de registro 

    if(dias_con_datos==1):
        operante = Decimal(28)
    elif(dias_con_datos==2):
        operante = Decimal(28/2)
    elif(dias_con_datos==3):
        operante = Decimal(28/3)
    elif(dias_con_datos==4):
        operante = Decimal(28/4)
    elif(dias_con_datos==5):
        operante = Decimal(28/5)
    elif(dias_con_datos==6):
        operante = Decimal(28/6)
    elif(dias_con_datos==7):
        operante = Decimal(28/7)

    print(f"Acumulado kwh: {resultado_total}")
    print(f"Consumo del mes: {round(resultado_total*operante, 6)}")

    print("Valor máximo de consumo:", max_consumo)
    print("Hora del valor máximo de consumo:", hora_max_consumo[0], ":", hora_max_consumo[1])

    ''' /*********************************/Termina el cálculo de datos para realizar el reporte\*********************************'''

    # SE RETORNA LA LISTA DE DATOS QUE SERÁ REVELANTE PARA GENERAR EL GRÁFICO
    return datos_consumo

# se asignan datos para realizar pruebas
# debemos asegurarnos de respetar los formatos de fecha
fecha_inicio = datetime(2024, 2, 24)
fecha_fin = datetime(2024, 3, 1)
medidor_id = "8096"

# se asignan datos para realizar pruebas
# debemos asegurarnos de respetar los formatos de fecha
# fecha_inicio = datetime(2024, 3, 1)
# fecha_fin = datetime(2024, 3, 4)
# medidor_id = "08119"

#obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)

# llamando a la funcion
datos_consumo = obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)

def generar_grafico_consumo_por_horas(datos):

    # Desempaquetar los datos
    horas = [f"{hora:02d}:{minuto:02d}" for hora, minuto, _ in datos]
    consumos = [consumo for _, _, consumo in datos]

    # se encuentra al índice que posee el dato del pico máximo
    indice_pico_maximo = consumos.index(max(consumos))
    # se guarda el valor de este dato en la variable
    hora_pico_maximo = horas[indice_pico_maximo]

    # se crea el gráfico
    # se crea el tamaño de la figura en la ventana
    plt.figure(figsize=(10, 6))

    # se proporcionan datos para el gráficos como el formato de línea, color y datos
    plt.plot(horas, consumos, color='tab:orange', linestyle='-')

    # se marca el punto con el máximo consumo
    plt.scatter(hora_pico_maximo, max(consumos), color='b', label=f'Máx. Demanda: {hora_pico_maximo} - kW {max(consumos):.8f}', zorder=5)
    
    # se añade data para las etiquetas y leyenda
    plt.title('Máxima demanda')
    plt.ylabel('Consumo de energía (kWh)')
    plt.xticks(range(0, len(horas), 4), rotation='vertical')
    plt.legend()

    # muestra el gráfico
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

generar_grafico_consumo_por_horas(datos_consumo)