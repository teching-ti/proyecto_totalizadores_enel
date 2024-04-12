
# El problema de que tus promedios tengan 95 elementos puede estar relacionado con cómo estás calculando los promedios. Analicemos el código para ver dónde podría estar ocurriendo esto.

# En tu código, estás calculando los promedios por hora y día utilizando el siguiente fragmento:

# Diccionario para almacenar los promedios por hora y día
promedios_por_hora_y_dia = defaultdict(list)

# Iterar sobre los registros
for registro in registros:
    # Crear una clave única para la fecha y la hora
    clave = (registro.date, registro.time)

    # Calcular el promedio de las corrientes
    corrientes = [registro.average_phase_a_current, registro.average_phase_b_current, registro.average_phase_c_current]
    corrientes_validas = [c for c in corrientes if c is not None]
    promedio = sum(corrientes_validas) / len(corrientes_validas) if corrientes_validas else None

    # Agregar el promedio al diccionario
    promedios_por_hora_y_dia[clave].append(promedio)

# Aquí estás calculando un promedio para cada registro, pero solo lo estás agregando al diccionario promedios_por_hora_y_dia si el promedio es diferente de None. Esto puede causar que algunos promedios no se agreguen si todos los valores de corriente para una hora específica son None, lo que puede resultar en que la lista de promedios tenga menos elementos de los esperados.

# Para solucionar esto, podrías considerar agregar None a la lista de promedios si no hay valores válidos para una hora específica. Esto garantizará que la lista de promedios tenga la misma longitud que la lista de horas. Aquí tienes cómo puedes hacerlo:

# Diccionario para almacenar los promedios por hora y día
promedios_por_hora_y_dia = defaultdict(list)

# Iterar sobre los registros
for registro in registros:
    # Crear una clave única para la fecha y la hora
    clave = (registro.date, registro.time)

    # Calcular el promedio de las corrientes
    corrientes = [registro.average_phase_a_current, registro.average_phase_b_current, registro.average_phase_c_current]
    corrientes_validas = [c for c in corrientes if c is not None]
    promedio = sum(corrientes_validas) / len(corrientes_validas) if corrientes_validas else None

    # Agregar el promedio al diccionario
    promedios_por_hora_y_dia[clave].append(promedio)

# Asegurarse de que cada lista de promedios tenga 96 elementos
for lista_promedios in promedios_por_hora_y_dia.values():
    while len(lista_promedios) < 96:
        lista_promedios.append(None)

#Esta modificación asegurará que cada lista de promedios tenga 96 elementos, lo que debería resolver el problema de tener menos elementos de los esperados en la lista de promedios.




