import os
from datetime import datetime, timedelta
from modelos import DatosMedidorConsumo
from db import SessionLocal
import re

def evaluar_guardar_archivos(lista_rutas):
    # creacion de la sesion para acceder a la base de datos
    archivos_no_validos = []
    db = SessionLocal()
    for ruta in lista_rutas:

        # con el dato de la ruta se obtiene solo el nombre del archivo
        nombre_archivo = os.path.basename(ruta)
        print(f"Analizando: {ruta}")

        # se obtiene la extension del archivo
        extension_archivo = os.path.splitext(nombre_archivo)[1]
        try:

            ''' CONDICION PARA EVALUAR SI UN ARCHIVO DEBE SER PROCESADO '''
            # estas condiciones podrían ser modificadas en base al nombre del archivo, depende de los archivos como tal
            # estas condiciones buscan que si un archivo es csv, su nombre debe iniciar con EDP, y si el archivo es prn su nombre debe iniciar con a
            # si no es así entonces no se abrirá dicho archivo y por lo tanto no se realizará su proceso de guardado respectivo
            ''' EVALUAR SIEMPRE EL TEMA DE LAS CONDICIONES, FRANK SOLIS, COMENTA QUE EL NOMBRE DE LOS ARCHIVOS (csv, QUE VENDRÍAN A SER LOS ELSTER)
            SIEMPRE INCIAN CON EDP; SIN EMBARGO, RESPONDIÓ TEXTUALMENTE: ".Para este primer avance solo se tiene A1800R", POR LO TANTO SE PUEDE 
            SOMETER A EVALUACIÓN LA SEGUNDA CONDICIÓN PARA LOS ARCHIVOS PRN '''
            if((extension_archivo == '.csv' and nombre_archivo.startswith("EDP")) or (extension_archivo == '.prn' and nombre_archivo.startswith("A"))):
                with open(ruta, 'r') as archivo:

                    '''esta porcion del codigo leerá solo la primera línea para detectar si el archivo esta separado por , o ;'''
                    separador = ''
                    primera_linea = archivo.readline()
                    if ',' in primera_linea:
                        separador = ','
                    elif ';' in primera_linea:
                        separador =  ';'
                    
                    # se lee el archivo linea por linea
                    for line in archivo:

                        # separa los valores de la línea por comas y elimina los espacios en blanco que se encuentra entre cada dato
                        # los guarda dentro de una lista llamada 'values'
                        values = [value.strip() for value in line.split(separador)]
                        #print(values)
                        
                        ''' ESTA CONDICION SOLO APLICA A LOS ARCHIVOS DE EXTENSIÓN CSV '''
                        if(extension_archivo == '.csv'):

                            # la variable 'identificador_elster' usa una expresión regular que eliminará todos los caracteres excepto los primeros numeros de values[0]
                            # osea del dato que se encuentra en la primera columna de cada fila
                            # luego ese dato que vendría a ser el identificador del meter se agrega como dato para guardar
                            meter_id_modificado = re.search(r'(\d+)', values[0]).group(1)

                            # se guarda en la variable date_str el valor de fecha que llega desde el archivo
                            date_str = values[1]

                            # el dato está como cadenena, por lo tanto se convierte al tipo de dato fecha
                            date = datetime.strptime(date_str, '%d/%m/%Y').date()

                            # se quitan las comillas del valor que llega desde el archivo para las horas
                            time_str = values[2].strip('"')

                            # existe la posibilidad de que la fecha llegue solo como horas y minutos, como también como horas, minutos y segundos
                            # entonces es recomendable evaluar la cantidad de caracteres para convertir a fecha
                            if len(time_str) <= 5:
                                time_edit = datetime.strptime(time_str, '%H:%M').time()
                            else:
                                time_edit = datetime.strptime(time_str, '%H:%M:%S').time()
                            time_obj = time_edit
                            # el dato está como cadenena, por lo tanto se convierte al tipo de dato time

                            # se establece en los datos numéricos que si se encuentran vacíos, estos se remplazarán por None   
                            # se crea un objeto data para insertar los valores obtenidos
                            # en caso de que no exista data para los campos numéricos
                            # se registra un valor None = Null
                            data = DatosMedidorConsumo(
                                meter_id=meter_id_modificado,
                                date=date,
                                time=time_obj,
                                kwh_del=float(values[3]) if values[3] else None,
                                kwh_rec=float(values[4]) if values[4] else None,
                                kvarh_q1=float(values[6]) if values[6] else None,
                                kvarh_q2=float(values[7]) if values[7] else None,
                                kvarh_q3=float(values[8]) if values[8] else None,
                                kvarh_q4=float(values[9]) if values[9] else None,
                            )
                            
                        elif(extension_archivo == '.prn'):

                            ''' ESTA CONDICION SOLO APLICA A LOS ARCHIVOS DE EXTENSIÓN PRN '''
                            # el identificador del meter es modificado para que no posee comillas ni espacios
                            meter_id_modificado = values[0].strip('" ')

                            # este metodo se ejecuta solo si el valor de fecha tiene una " por delante, osea si tiene el formato que traen los prn
                            # values[1] representa a la columna de fecha
                            # se retiran las comillas y se guardan en date_str
                            date_str = values[1].strip('"')

                            # convierte la fecha al formato de la base de datos (YYYY-MM-DD)
                            date = datetime.strptime(date_str, '%d/%m/%y').date()

                            #es necesario modificar los datos de la hora para que se guarde como tal, el archivo nos lo proporciona como un texto
                            #y es importante guardarlo como el tipo de dato correcto.
                            # sucede algo más, y es que para el campo de hora, los archivos prn, manejan el 24:00, se debe convertir a 00:00:00
                            # se retiran las comillas
                            time_str = values[2].strip('"')

                            # se valida que el dato inicie con 24
                            if time_str.startswith('24:'):

                                # aumenta en 1 el día cuando se llega a las 24 horas
                                date += timedelta(days=1)

                                # reemplaza el 24 por 00 desde antes del indice 2 de la cadena
                                time_str = '00' + time_str[2:]
                            # se guarda la cadena en un formato de tipo time    
                            time_obj = datetime.strptime(time_str, '%H:%M').time()

                            # se crea un objeto data para insertar los valores obtenidos
                            # en caso de que no exista data para los campos numéricos
                            # se registra un valor None = Null
                            data = DatosMedidorConsumo(
                                meter_id=values[0].strip('" '),
                                date=date,
                                time=time_obj,
                                kwh_del=float(values[4]) if values[4] else None,
                                kwh_rec=float(values[5]) if values[5] else None,
                                kvarh_q1=float(values[6]) if values[6] else None,
                                kvarh_q2=float(values[7]) if values[7] else None,   
                                kvarh_q3=float(values[8]) if values[8] else None,
                                kvarh_q4=float(values[9]) if values[9] else None,
                            )

                        # estas líneas verifican si ya existe un registro con la misma clave primaria antes de poder insertar
                        # se busca por medio de una consulta usando parámetros del nuevo dato, si es que estos ya existen
                        # entonces devolverá información y se guardará en la variable 'existing_record', en caso de que no
                        # exista entonces no contendrá información
                        existing_record = db.query(DatosMedidorConsumo).filter_by(
                            meter_id=data.meter_id,
                            date=data.date,
                            time=data.time
                        ).first()

                        # se valida la data de 'existing_record'
                        if existing_record:
                            # en caso de que ya exista un registro con la misma clave primaria, no se inserta
                            print(f"Registro duplicado encontrado y omitido: {data}")
                        else:
                            # si no existe, entonces se podrá insertar el nuevo registro
                            # se agregan los datos de la sesion para acceder a la base de datos
                            db.add(data)

                    # el commit añade todo lo que se ha obtenido, si hay un error en algún objeto, entonces no se guarda nada
                    db.commit()
            else:
                # esto aplica solo a los archivos que no puedieron ser evaluados por no cumplir con el formato o con el nombre
                # se añaden los archivos no validos por error de valor a la lista
                archivos_no_validos.append(nombre_archivo)
        except ValueError:
            # se añaden los archivos no validos por error de valor a la lista
            archivos_no_validos.append(nombre_archivo)

            # deshace las operaciones pendientes, revierte todo lo relacionado en la sesion
            # hasta el último commit
            db.rollback()
        except Exception as e:
            # se añaden los archivos no validos por error de valor a la lista
            archivos_no_validos.append(nombre_archivo)

            # deshace las operaciones pendientes, revierte todo lo relacionado en la sesion
            # hasta el último commit
            db.rollback()
            print(f"Error al procesar el archivo {nombre_archivo}: {str(e)}")
    
    # se cierra la sesion de la base  de datos
    db.close()
    #"se retorna una lista de archivos no validos, osea los que según el filtro principal, no cumplen con las condiciones para abrir el archivo"
    # si la lista esta vacia o contiene datos, ejecutará una acción en 'interfaz.py'
    return archivos_no_validos