from sqlalchemy import func
from db import session
from datetime import datetime,  timedelta
from modelos  import DatosMedidorConsumo
import matplotlib.pyplot as plt
from decimal import Decimal
import calendar

def obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id):

    sumatoria_total = []
    # Consulta a la base de datos
    consulta = session.query(
    DatosMedidorConsumo.date,
    func.HOUR(DatosMedidorConsumo.time).label('hora'),
    func.MINUTE(DatosMedidorConsumo.time).label('minuto'),
    func.sum(DatosMedidorConsumo.kwh_del).label('consumo')
    ).filter(
        DatosMedidorConsumo.date >= fecha_inicio,
        DatosMedidorConsumo.date <= fecha_fin,
        DatosMedidorConsumo.meter_id == medidor_id
    ).group_by(
        DatosMedidorConsumo.date,
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time) / 15
    ).order_by(
        DatosMedidorConsumo.date,
        func.HOUR(DatosMedidorConsumo.time),
        func.MINUTE(DatosMedidorConsumo.time)
    )
    
    # se ejecuta la consulta
    resultados = consulta.all()

    # selecciona al primer dato de las fechas
    fecha_inicio_consulta = resultados[0].date

    # se busca si hay algún dato correspondiente a las 00:00 horas del primer día
    primer_dia_datos = [resultado for resultado in resultados if resultado.date == fecha_inicio_consulta and resultado.hora == 0 and resultado.minuto == 0]

    # si hay datos correspondientes a las 00:00 horas del primer día, los eliminamos de la lista de resultados
    if primer_dia_datos:
        resultados = [resultado for resultado in resultados if resultado not in primer_dia_datos]

    # selecciona al último dato de las fechas
    ultimo_dia = resultados[-1].date

    # agregar datos en una nueva variable de resultados
    nuevos_resultados = []
    for resultado in resultados:
        if resultado.date != ultimo_dia or (resultado.date == ultimo_dia and (resultado.hora == 0 and resultado.minuto == 0)):
            nuevos_resultados.append(resultado)

    resultados = nuevos_resultados

    # for resultado in resultados:
    #     print(resultado.date, resultado.hora, resultado.minuto, resultado.consumo)
    # la variable resultados contiene dato por dato, se encontrar la hora 00 y el minuto 00 del primer día para no usarlo y solo el 00:00 del último día para tambiéin poder usarlo

    # print(resultados)
    # usamos una comprensión de lista para iterar sobre los resultados de la consulta anterior, por cada resultado se crea una tupla
    # que contiene la hora, minuto y consumo total, estas tuplas se agregan a una lista llamada 'datos_consumo'
    datos_consumo = [(resultado.hora, resultado.minuto, resultado.consumo) for resultado in resultados]

    ''' /*********************************/Desde este punto se obtendrán datos para realizar el reporte\*********************************'''
    # Diccionario para almacenar el consumo total por hora
    consumo_por_hora = {}
    sumatoria_total = []

    # Recorrer los resultados y calcular el consumo total por hora
    for resultado in resultados:
        hora = resultado.hora
        minuto = resultado.minuto
        consumo = resultado.consumo

        # Calcular la hora redondeada hacia abajo al cuarto de hora más cercano
        hora_redondeada = hora + minuto / 60

        # Sumar el consumo total al total de esa hora
        #consumo_por_hora[hora_redondeada] = consumo_por_hora.get(hora_redondeada, 0) + consumo_total
        if consumo is not None:
            consumo_por_hora[hora_redondeada] = consumo_por_hora.get(hora_redondeada, 0) + consumo


    # Imprimir los resultados
    for hora_redondeada, consumo in sorted(consumo_por_hora.items()):
        hora = int(hora_redondeada)
        minutos = int((hora_redondeada % 1) * 60)
        # aqui se obtienen los valores totales ya sumados
        '''
        DEVUELVE INFORMACIÓN SIMILAR A ESTA, LA CUAL SERÍA DATA YA SUMADA EN DONDE EL VALOR DEL 00:00 ES LA SUMA DE TODOS LOS DÍAS
        00:00 0.16640000
        00:15 0.16467500
        00:30 0.15812500
        '''
        #print(f"{hora:02d}:{minutos:02d}", consumo)
        sumatoria_total.append(consumo)
    
    #print(f"Esta es la sumatoria total de datos vacios: {sumatoria_total}")

    # Encontrar la hora con el máximo consumo y su valor correspondiente
    # hora
    hora_max_consumo = max(consumo_por_hora, key=consumo_por_hora.get)
    # valor de máximo consumo con dicha hora
    # max_consumo = consumo_por_hora[hora_max_consumo]

    # se crea una variable que almacenará la suma de los elementos en la lista
    resultado_total = sum(sumatoria_total)
    # consulta para obtener el numero de días de los que se tiene registro en el rango de fechas seleccionado
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
    # imprimiendo numero de dias que cuentan con data
    # print(consulta_numero_dias.first())

    # se guarda la información obtenida en una variable
    resultado_n_dias = consulta_numero_dias.first()
    # se guarda específicamente el número de días ya que el resultado como columna a mostrar fue 'dias_unicos'
    dias_con_datos = resultado_n_dias.dias_unicos - 1
    # se compara el número de días con los que se tiene registro, esto a fin de obtener un cálculo mensual
    # este ejemplo es para febrero, obtener el mes de registro

    # obtener días por mes
    # CALCULAR A QUÉ MES PERTENECE Y EJECUTAR EL CALCULO DEL MES

    '''agregado inicia'''
    # Calcula el número total de días en el rango de fechas seleccionado
    total_dias = (fecha_fin - fecha_inicio).days +1

    # Diccionario para almacenar el número de días por mes
    dias_por_mes = {}

    # Itera sobre cada día en el rango y cuenta cuántos días hay por mes
    for i in range(total_dias):
        fecha = fecha_inicio + timedelta(days=i)
        mes = fecha.month
        dias_por_mes[mes] = dias_por_mes.get(mes, 0) + 1

    # Determina el mes predominante
    mes_predominante = max(dias_por_mes, key=dias_por_mes.get)

    # Calcula el número de días del mes predominante
    dias_mes_predominante = dias_por_mes.get(mes_predominante, 0)

    # Determina si hay más días en el mes predominante o en el siguiente mes
    if dias_mes_predominante > total_dias / 2:
        dias_mes = calendar.monthrange(fecha_inicio.year, mes_predominante)[1]
    else:
        # Si el mes siguiente tiene más días, usa su cantidad de días
        siguiente_mes = (fecha_fin.replace(day=1) + timedelta(days=32)).replace(day=1).month
        dias_mes = calendar.monthrange(fecha_fin.year, siguiente_mes)[1]

    # Ajusta el número de días para febrero si es necesario
    if mes_predominante == 2:
        dias_mes = min(dias_mes, 28)
    '''agregado final'''
    #print(dias_mes)


    ''' Datos de vacíos '''
    contador_vacios = 0
    # Variables para almacenar la fecha y hora del primer y último vacío
    fecha_hora_primer_vacio = None
    fecha_hora_ultimo_vacio = None

    # Iterar sobre los resultados
    for resultado in resultados:
        # Verificar si el consumo es NULL
        if resultado.consumo is None:
            contador_vacios += 1
            # Obtener la fecha y hora del primer vacío
            if fecha_hora_primer_vacio is None:
                fecha_hora_primer_vacio = f"{resultado.date} {resultado.hora}:{resultado.minuto}"
            # Almacenar la fecha y hora del último vacío en cada iteración
            fecha_hora_ultimo_vacio = f"{resultado.date} {resultado.hora}:{resultado.minuto}"

    if resultado_total != 0:
        if dias_con_datos == 1:
            operante = Decimal(dias_mes)
        else:
            operante = Decimal(dias_mes / (dias_con_datos))
        
        # consumo total del mes
        consumo_mes = round(resultado_total * operante, 6)
        
        # hora en la que se registra una mayor cantidad de consumo, sumando todos los días seleccionados
        hora_max = int(hora_max_consumo)
        min_max = int((hora_max_consumo % 1) * 60)
        hora_max_formateada =  f"{hora_max}:{min_max:02}"

        # es importante obtener el tipo de consumo
        tipo_consumo = "En proceso"

        #hora de maximo consumo
        lista_resultados = [medidor_id, dias_con_datos, mes_predominante, contador_vacios, fecha_hora_primer_vacio, fecha_hora_ultimo_vacio, resultado_total, consumo_mes, hora_max_formateada, tipo_consumo]
        #print(f"El consumo total del mes se calcula con el resultado total multiplicado por:{operante} ")
        '''
        print(f"Medidor ID: {medidor_id}")
        print(f"Rango de Fechas Seleccionadas:\nDesde: {fecha_inicio}\nHasta: {fecha_fin}")
        print(f"Dias con registro de consumo: {dias_con_datos}")
        print(f"Mes: {mes_predominante}")
        print(f"Acumulado kWh: {resultado_total}")
        print(f"Consumo del mes: {consumo_mes}")
        '''
        #print("Valor máximo de consumo:", max_consumo)
        '''
        print("Hora del valor máximo de consumo:",hora_max_consumo )
        print("Hora del valor máximo de consumo:", int(hora_max_consumo), ":", int((hora_max_consumo % 1) * 60))
        print("\nDatos de Vacíos")
        print("Número de vacíos:", contador_vacios)
        print("Fecha y hora del primer vacío:", fecha_hora_primer_vacio)
        print("Fecha y hora del último vacío:", fecha_hora_ultimo_vacio)
        print("\n")
        '''

        # print("Valor máximo de consumo:", max_consumo)
        # print("Hora del valor máximo de consumo:", hora_max_consumo[0], ":", hora_max_consumo[1])
    else:
        print("No se puede entregar un gráfico debido a que todos los datos en este rango de fecha se encuentran vacíos")

    ''' /*********************************/Termina el cálculo de datos para realizar el reporte\*********************************'''

    # SE RETORNA LA LISTA DE DATOS QUE SERÁ RELEVANTE PARA GENERAR EL GRÁFICO
    #return datos_consumo
    return lista_resultados

# se asignan datos para realizar pruebas
# debemos asegurarnos de respetar los formatos de fecha
'''pruebas manuales, actualmente ya se pueden realizar estas pruebas desde el aplicativo'''
# fecha_inicio = datetime(2024, 2, 24)
# fecha_fin = datetime(2024, 3, 1)
# medidor_id = "8096"

# fecha_inicio = datetime(2024, 3, 16)
# fecha_fin = datetime(2024, 3, 22)
# medidor_id = "8162"

# se asignan datos para realizar pruebas
# debemos asegurarnos de respetar los formatos de fecha
#fecha_inicio = datetime(2024, 3, 1)
#fecha_fin = datetime(2024, 3, 4)
#medidor_id = "08119"

#obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)

# llamando a la funcion
#datos_consumo = obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)

def generar_grafico_consumo_por_horas(datos):

    # Desempaquetar los datos
    horas = [f"{hora:02d}:{minuto:02d}" for hora, minuto, _ in datos]
    consumos = [consumo for _, _, consumo in datos]

    print("Datos: \n")
    print(datos)
    # se encuentra al índice que posee el dato del pico máximo  
    try:        
        indice_pico_maximo = consumos.index(max(consumos))
        # se guarda el valor de este dato en la variable
        hora_pico_maximo = horas[indice_pico_maximo]

        # se crea el gráfico
        # se crea el tamaño de la figura en la ventana
        fig = plt.figure(figsize=(10, 6))

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
        #plt.show()
        return fig
    except:
        return None

#generar_grafico_consumo_por_horas(datos_consumo)