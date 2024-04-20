from sqlalchemy import func, and_
from datetime import time
import os
from db import SessionLocal
from modelos  import  Medidores, DatosMedidorInstrumentacion
import matplotlib.pyplot as plt
from datetime import timedelta
from tkinter import messagebox

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

        if(registros):

            # primer valor de la respuesta obtenida del medidor que esta siendo evaluado
            primer_registro = registros[0]
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
                
                #print(promedio_factor)
                # Agregar los datos procesados al diccionario
                if fecha not in datos_procesados:
                    datos_procesados[fecha] = []
                datos_procesados[fecha].append((hora.hour * 60 + hora.minute, promedio_factor))

            '''PRIMER GRAFICO DE PROMEDIOS INICIA'''    
            for fecha in datos_procesados.keys():
                # Obtener la fecha del día siguiente
                fecha_siguiente = fecha + timedelta(days=1)

                # Verificar si existe datos para la fecha siguiente
                if fecha_siguiente in datos_procesados:
                    # Obtener los datos de las 00:00 horas del día siguiente
                    datos_siguiente = datos_procesados[fecha_siguiente]

                    # Mover el primer dato del día siguiente al final del día actual
                    primer_dato_siguiente = datos_siguiente[0]
                    datos_procesados[fecha].append(primer_dato_siguiente)
                    #print(f"Se movió el primer dato del día siguiente ({fecha_siguiente}) al final del día actual ({fecha}).")

                    # Eliminar el primer dato del día siguiente
                    datos_procesados[fecha_siguiente] = datos_siguiente[1:]
                    #print(f"Se eliminó el primer dato del día siguiente ({fecha_siguiente}).")
            
            if not datos_procesados[fecha_fin]:
                # Eliminar el último día del conjunto de datos procesados
                del datos_procesados[fecha_fin]
            
            # Imprimir los datos procesados
            # for fecha, datos in datos_procesados.items():
            #     print(f"Fecha: {fecha}, Datos: {datos}")

            # Inicializar listas para almacenar los valores por día y las fechas
            valores_por_dia = []
            fechas = []
            horas_por_dia = []

            # Recorrer los datos procesados y organizar los valores por día
            for fecha, valores in datos_procesados.items():
                horas = [f"{hora // 60:02d}:{hora % 60:02d}" for hora, _ in valores]  # Formatear las horas como "HH:MM"
                valores_dia = [valor for _, valor in valores]  # Obtener los valores para este día
                horas_por_dia.append(horas)  # Agregar las horas formateadas a la lista de horas por día
                valores_por_dia.append(valores_dia)  # Agregar los valores a la lista de valores por día
                
                fecha_legible = fecha.strftime('%d/%m/%Y')  # Formato dd/mm/yyyy
                dia_semana = fecha.strftime('%a')

                # Crear una etiqueta legible para la leyenda
                etiqueta = f'{fecha_legible}'
                fechas.append(etiqueta)
            '''PRIMER GRAFICO DE PROMEDIOS FINALIZA'''

            for i, valores_dia in enumerate(valores_por_dia, start=1):
                print(f"Longitud de horas_por_dia en la iteración {i}: {len(horas_por_dia[i-1])}")
                print(f"Longitud de valores_dia en la iteración {i}: {len(valores_dia)}")

            #print(horas_por_dia)

            # Inicializar un diccionario para almacenar la suma de valores de corriente por hora
            '''SEGUNDO GRAFICO DE PROMEDIOS INICIA'''
            suma_valores_por_hora = {}
            num_dias_por_hora = {}

            # Iterar sobre los datos procesados
            for fecha, valores in datos_procesados.items():
                # Iterar sobre los valores para cada fecha
                for hora, valor in valores:
                    # Sumar el valor de corriente al diccionario correspondiente a la hora actual
                    if hora not in suma_valores_por_hora:
                        suma_valores_por_hora[hora] = valor
                        num_dias_por_hora[hora] = 1
                    else:
                        suma_valores_por_hora[hora] += valor
                        num_dias_por_hora[hora] += 1

            # Calcular el promedio para cada hora del día
            promedio_por_hora = {}
            for hora, suma_valores in suma_valores_por_hora.items():
                num_dias = num_dias_por_hora[hora]
                promedio_por_hora[hora] = suma_valores / num_dias if num_dias > 0 else None

            # Imprimir el promedio por hora
            # for hora, promedio in promedio_por_hora.items():
            #     print(f"Promedio de corriente para la hora {hora:02d}:00: {promedio}")
            #print(promedio_por_hora)

            # Convertir el diccionario promedio_por_hora en listas separadas de horas y valores
            horas_promedio = list(promedio_por_hora.keys())
            valores_promedio = list(promedio_por_hora.values())
            # Convertir las horas a formato HH:MM
            horas_promedio = [f"{hora // 60:02d}:{hora % 60:02d}" for hora in horas_promedio]

            '''SEGUNDO GRAFICO DE PROMEDIOS FINALIZA'''


            # Crear una nueva figura para el segundo gráfico debajo del primer gráfico
            plt.figure(figsize=(12, 8))

            '''PRIMER GRAFICO'''
            # Agregar el primer gráfico en la parte superior
            plt.subplot(2, 1, 1)  # 2 filas, 1 columna, primer gráfico
            for i, valores_dia in enumerate(valores_por_dia, start=1):
                plt.plot(horas_por_dia[0], valores_dia, label=fechas[i-1])
                plt.xticks(range(0, len(horas_por_dia[0]), 5), rotation=45)
            #plt.title('Gráfico de Perfiles de Instrumentación')
            plt.xlabel('Hora')
            plt.ylabel('Corriente')
            plt.legend()
            plt.grid(linestyle="dashed")
            
            '''SEGUNDO GRAFICO'''
            # Agregar el segundo gráfico en la parte inferior
            plt.subplot(2, 1, 2)  # 2 filas, 1 columna, segundo gráfico
            plt.plot(horas_promedio, valores_promedio, color='tab:blue', label='Promedio')
            plt.xticks(range(0, len(horas_promedio), 5), rotation=45)
            plt.xlabel('Hora')
            plt.ylabel('Corriente')
            plt.legend()
            plt.grid(linestyle="dashed")

            plt.tight_layout()  # Ajustar el espaciado entre subgráficos

            # Obtener la ruta de la carpeta de descargas en Windows
            carpeta_graficos = os.path.join(os.environ["USERPROFILE"], "Downloads", "APLICATIVO_ENEL_SUMINISTROS_REPORTES", "GRAFICAS_SUMINISTROS")

            # Verificar si la carpeta de descargas existe
            if not os.path.exists(carpeta_graficos):
                # Si la carpeta no existe, crearla
                os.makedirs(carpeta_graficos)

            # Luego, al guardar la figura, especifica la ruta completa de la carpeta de descargas
            nombre_archivo = f"{carpeta_graficos}/{medidor_id}_{fecha_inicio}_{fecha_fin}.png"
            plt.savefig(nombre_archivo)

            #plt.show()
        else:
            messagebox.showerror(f"Registros incorrectos - {medidor_id}", "No se pudo generar la gráfica debido a que no se cuenta con los datos de perfil de instrumentación.\nSe recomienda importar el perfil de instrumentación requerido")



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