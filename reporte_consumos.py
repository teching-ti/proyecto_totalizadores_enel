from sqlalchemy import func
from db import session
from datetime import datetime,  timedelta
from modelos  import DatosMedidorConsumo
import matplotlib.pyplot as plt
from decimal import Decimal
import calendar
import numpy as np
fechas_excedentes = []

def obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id):
    # try:
    sumatoria_total = []
    # consulta a la base de datos
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

    '''
    ESTA SECCION EVALÚA SI LA FECHA SELECCIONADA POR EL USUARIO EXCEDE A LA FECHA DE REGISTROS CON LA QUE CUENTA EL MEDIDOR EN CUESTIÓN,
    DE CUMPLIRSE SE PROCEDEDERÁ A ENVIAR DATA PARA MOSTRAR DESDE LA INTERFAZ MAIN.PY, SE DEBERÍA DE ALMACENAR EN UNA LISTA, INDICANDO LAS FECHAS Y MEDIDOR 
    CON EL MENSAJE DE AVISO, A FIN DE EVITAR MENSAJES DE ERROR
    '''
    #print(f"Ultimo dia de registro {ultimo_dia}")
    #print(f"Ultimo dia de seleccion por el usuario {fecha_fin}")
 
    if ultimo_dia<fecha_fin:
        fechas_excedentes.append(medidor_id)

    '''Definir la función que recibirá este dato'''
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
    # almacenará el consumo total por cada hora del día
    consumo_por_hora = {}

    # almacenará los valores totales ya sumados
    sumatoria_total = []

    # se recorre la lista de resultados, se brinda información sobre la hora, minuto y consumo asociado
    for resultado in resultados:
        hora = resultado.hora
        minuto = resultado.minuto
        consumo = resultado.consumo

        # calcular la hora redondeada hacia abajo al cuarto de hora más cercano
        hora_redondeada = hora + minuto / 60

        # se suma al diccionario el consumo al total de la hora que se esta evaluando
        if consumo is not None:
            consumo_por_hora[hora_redondeada] = consumo_por_hora.get(hora_redondeada, 0) + consumo

    # se agrega el dato de consumo por hora
    datos_consumo_por_hora = []
    valores_horas = []
    
    #print(medidor_id)
    # se ordena la hora para mejor visualización de los datos
    for hora_redondeada, consumo in sorted(consumo_por_hora.items()):
        hora = int(hora_redondeada)
        minutos = int((hora_redondeada % 1) * 60)

        '''se agrega elemento para validar la información de los suministros'''
        # se agrega el dato de consumo por hora
        datos_consumo_por_hora.append((hora, minutos, consumo))
        '''se agrega elemento para validar la información de los suministros'''


        # aqui se obtienen los valores totales ya sumados
        '''
        DEVUELVE INFORMACIÓN SIMILAR A ESTA, LA CUAL SERÍA DATA YA SUMADA EN DONDE EL VALOR DEL 00:00 ES LA SUMA DE TODOS LOS DÍAS
        00:00 0.16640000
        00:15 0.16467500
        00:30 0.15812500
        '''
        # consumo sería el valor número del conjunto de días sumados, pero en base a una hora en específico
        # por esa razón es necesario que en cada bucle se añada a la lista 'suma_total'
        # en este apartado se imprime la suma total de todos los días seleccionados por horas, con lo que se imprime
        # se puede obtener facilmente la hora de máximo consumo
        print(f"{hora:02d}:{minutos:02d} {consumo}")
        valores_horas.append(f"{hora:02d}:{minutos:02d}-{consumo}")
        # se extrae el valor de conusmo y se agrega a la lista sumatoria total, esto representará el consumo total por horas
        sumatoria_total.append(consumo)

    #print(datos_consumo_por_hora)
    #print(f"Esta es la sumatoria total de datos vacios: {sumatoria_total}")

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
    # se calcula el número total de días en el rango de fechas seleccionado
    total_dias = (fecha_fin - fecha_inicio).days +1

    # diccionario para almacenar el número de días por mes
    dias_por_mes = {}

    # iterando sobre cada día en el rango y cuenta cuántos días hay por mes
    for i in range(total_dias):
        fecha = fecha_inicio + timedelta(days=i)
        mes = fecha.month
        dias_por_mes[mes] = dias_por_mes.get(mes, 0) + 1

    # determina cual el mes predominante
    mes_predominante = max(dias_por_mes, key=dias_por_mes.get)

    # calcula el número de días del mes predominante
    dias_mes_predominante = dias_por_mes.get(mes_predominante, 0)

    # determina si hay más días en el mes predominante o en el siguiente mes
    if dias_mes_predominante > total_dias / 2:
        dias_mes = calendar.monthrange(fecha_inicio.year, mes_predominante)[1]
    else:
        # si el mes siguiente tiene más días, usa su cantidad de días
        # se evalúa en base al registro, por ejemplo si se selcciona una fecha entre el 28 marzo
        # en este caso al ser 7 días se usarían datos desde el 28 de marzo al 3 de abril,
        # en el grupo de días de marzo se tiene un total de cuatro días mientras que el segundo grupo
        # solo representa tres días, el valor a tomar según este ejemplo al mes de marzo
        siguiente_mes = (fecha_fin.replace(day=1) + timedelta(days=32)).replace(day=1).month
        dias_mes = calendar.monthrange(fecha_fin.year, siguiente_mes)[1]

    # se ajusta el número de días para febrero si es necesario
    if mes_predominante == 2:
        dias_mes = min(dias_mes, 28)
    '''agregado final'''
    #print(dias_mes)

    ''' Datos de vacíos '''
    contador_vacios = 0
    # se inican variables para almacenar la fecha y hora del primer y último vacío
    fecha_hora_primer_vacio = None
    fecha_hora_ultimo_vacio = None

    # iterando sobre los resultados
    for resultado in resultados:
        # verifica si el consumo es NULL
        if resultado.consumo is None:
            contador_vacios += 1
            # obtiene la fecha y hora del primer vacío
            if fecha_hora_primer_vacio is None:
                fecha_hora_primer_vacio = f"{resultado.date} {resultado.hora}:{resultado.minuto}"
            # almacena la fecha y hora del último vacío en cada iteración
            fecha_hora_ultimo_vacio = f"{resultado.date} {resultado.hora}:{resultado.minuto}"

    # se halla la hora con el máximo consumo y su valor correspondiente
    hora_max_consumo = max(consumo_por_hora, key=consumo_por_hora.get)
    hora_max = int(hora_max_consumo)
    min_max = int((hora_max_consumo % 1) * 60)

    # hora en la que se registra una mayor cantidad de consumo, sumando todos los días seleccionados
    hora_max_formateada =  f"{hora_max}:{min_max:02}"
    # valor de máximo consumo con dicha hora
    # max_consumo = consumo_por_hora[hora_max_consumo]

    '''INTENTANDO HALLAR EL TIPO DE SUMINISTRO INICIA'''
    # a evaluar
    ######### - dividir en 4 franjas los 96 datos
    ######### - madrugada, mañana, tarde, noche
    # variable para almacenar el tipo de consumo
    tipo_consumo = None
    print("-----")
    #print(valores_horas)
    madrugada = valores_horas[0:23]
    madrugada = sum([float(valor.split("-")[1]) for valor in madrugada])
    mañana = valores_horas[24:48]
    mañana = sum([float(valor.split("-")[1]) for valor in mañana])
    tarde = valores_horas[49:73]
    tarde = sum([float(valor.split("-")[1]) for valor in tarde])
    noche = valores_horas[74:96]
    noche = sum([float(valor.split("-")[1]) for valor in noche])
    
    # continuar...

    '''INTENTANDO HALLAR EL TIPO DE SUMINISTRO TERMINA'''

    # se crea una variable que almacenará la suma de los elementos en la lista, lo que sería el acumulado en todo el rango de fechas seleccionado
    resultado_total = sum(sumatoria_total)
    # sumatoria total 

    if resultado_total != 0:
        if dias_con_datos == 1:
            operante = Decimal(dias_mes)
        else:
            # número de días que posee el mes dividido por el número de días con datos
            operante = Decimal(dias_mes / (dias_con_datos))
        
        # consumo total del mes
        consumo_mes = round(resultado_total * operante, 6)
    
        # es importante obtener el tipo de consumo
        #tipo_consumo = "En proceso"

        #hora de maximo consumo
        lista_resultados = [medidor_id, dias_con_datos, mes_predominante, contador_vacios, fecha_hora_primer_vacio, fecha_hora_ultimo_vacio, resultado_total, consumo_mes, hora_max_formateada, tipo_consumo, fechas_excedentes]
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
    print("\n")
    # SE RETORNA LA LISTA DE DATOS QUE SERÁ RELEVANTE PARA GENERAR EL GRÁFICO
    #return datos_consumo
    return lista_resultados
    # except:
    #     print("No se pudo completar la operación, inténtelo nuevamente y revise los rangos de fecha seleccionados")