import os
from datetime import datetime, timedelta
from modelos import DatosMedidorConsumo, DatosMedidorInstrumentacion, Medidores
from db import SessionLocal
import re
import pandas as pd
from sqlalchemy.exc import IntegrityError

# Evaluar los perfiles de carga para realizar el guardado en la db

'''
Desarollar script para cargar excel con medidores y factores (definir columnas para insertar solo datos correspondientes)
UPDATE `medidores` SET `id`='[value-1]',`factor`='[value-2]' WHERE 1
->Script para actualizar el valor de cada medidor, 60, 100, 140, 200, 300, 400
'''

# esta función se utiliza para guardar en la base de datos información proveniente de los perfiles de carga e instrumentación (no almacena el id de los medidores)
# usa la tabla datos_medidores_consumo(perfiles de carga) y datos_medidores_instrumentación(perfiles de instrumentación)
def evaluar_guardar_archivos(lista_rutas):
    perfil = ""

    # creacion de la sesion para acceder a la base de datos
    archivos_no_validos = []

    #conexión a la base de datos a través de la sesion local
    db = SessionLocal()

    for ruta in lista_rutas:
        # con el dato de la ruta se obtiene solo el nombre del archivo
        nombre_archivo = os.path.basename(ruta)
        '''//////****** Muestra en pantalla el archivo que esta siendo revisado'''
        # print(f"Analizando: {ruta}")
        # se obtiene la extension del archivo
        extension_archivo = os.path.splitext(nombre_archivo)[1]
        try:
            ''' CONDICION PARA EVALUAR SI UN ARCHIVO DEBE SER PROCESADO '''
            # estas condiciones podrían ser modificadas en base al nombre del archivo, depende de los archivos como tal
            # estas condiciones buscan que si un archivo es csv, su nombre debe iniciar con EDP, y si el archivo es prn su nombre debe iniciar con a
            # si no es así entonces no se abrirá dicho archivo y por lo tanto no se realizará su proceso de guardado respectivo
            
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
                            perfil = "carga"
                            # la variable 'identificador_elster' usa una expresión regular que eliminará todos los caracteres excepto los primeros numeros de values[0]
                            # osea del dato que se encuentra en la primera columna de cada fila
                            # luego ese dato que vendría a ser el identificador del meter se agrega como dato para guardar
                            '''modificacion para los perfiles de carga'''
                            
                            # se colocó el {0*} en la expresión regular para retirar el 0 que llegaba por delante en el csv de 08119
                            meter_id_modificado = re.search(r'0*(\d+)', values[0]).group(1)

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
                            # perfiles de instrumentación
                            if nombre_archivo.endswith("_1.prn"):

                                perfil = "instrumentacion"
                                # se realizan modiifcaciones en la logica de guardar datos.
                                # se debe revisar cuantas columnas se tiene en la primera fila, de ser mayores que 13 entonces tiene A, B y C,
                                # la lógica debería de ser diferente según el caso

                                meter_id_modificado = values[0].strip('" ')
                                date_str = values[1].strip('"')

                                # convierte la fecha al formato de la base de datos (YYYY-MM-DD)
        
                                if len(date_str.split("/")[-1])<4:
                                    date = datetime.strptime(date_str, '%d/%m/%y').date()
                                else:
                                    date = datetime.strptime(date_str, '%d/%m/%Y').date()
                                
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

                                if len(values)>13:
                                    data = DatosMedidorInstrumentacion(
                                        meter_id=meter_id_modificado,
                                        date=date,
                                        time=time_obj,
                                        int_len=float(values[3]) if values[3] else None,
                                        average_phase_a_voltage = float(values[4]) if values[4] else None,
                                        average_phase_b_voltage = float(values[5]) if values[5] else None,
                                        average_phase_c_voltage = float(values[6]) if values[6] else None,
                                        average_phase_a_current = float(values[7]) if values[7] else None,
                                        average_phase_b_current = float(values[8]) if values[8] else None,
                                        average_phase_c_current = float(values[9]) if values[9] else None,

                                        end_phase_a_pf = float(values[10]) if values[10] else None,
                                        end_phase_b_pf = float(values[11]) if values[11] else None,
                                        end_phase_c_pf = float(values[12]) if values[12] else None,

                                        average_line_frequency = float(values[13]) if values[13] else None,

                                        average_phase_a_kw = float(values[14]) if values[14] else None,
                                        average_phase_b_kw = float(values[15]) if values[15] else None,
                                        average_phase_c_kw = float(values[16]) if values[16] else None,
                                    )
                                else:
                                    # print(values)
                                    # se debe crear una variable data diferente
                                    data = DatosMedidorInstrumentacion(
                                        meter_id=meter_id_modificado,
                                        date=date,
                                        time=time_obj,
                                        int_len=float(values[3]) if values[3] else None,
                                        average_phase_a_voltage = float(values[4]) if values[4] else None,
                                        average_phase_b_voltage = None,
                                        average_phase_c_voltage = float(values[5]) if values[5] else None,
                                        average_phase_a_current = float(values[6]) if values[6] else None,
                                        average_phase_b_current = None,
                                        average_phase_c_current = float(values[7]) if values[7] else None,

                                        end_phase_a_pf = float(values[8]) if values[8] else None,
                                        end_phase_b_pf = None,
                                        end_phase_c_pf = float(values[9]) if values[9] else None,

                                        average_line_frequency = float(values[10]) if values[10] else None,

                                        average_phase_a_kw = float(values[11]) if values[11] else None,
                                        average_phase_b_kw = None,
                                        average_phase_c_kw = float(values[12]) if values[12] else None,
                                    )
                            
                            #perfiles de carga prn
                            else:
                                perfil = "carga"
                                ''' ESTA CONDICION SOLO APLICA A LOS ARCHIVOS DE EXTENSIÓN PRN '''
                                # el identificador del meter es modificado para que no posee comillas ni espacios
                                meter_id_modificado = values[0].strip('" ')

                                # este metodo se ejecuta solo si el valor de fecha tiene una " por delante, osea si tiene el formato que traen los prn
                                # values[1] representa a la columna de fecha
                                # se retiran las comillas y se guardan en date_str
                                date_str = values[1].strip('"')

                                # convierte la fecha al formato de la base de datos (YYYY-MM-DD)
                                if len(date_str.split("/")[-1])<4:
                                    date = datetime.strptime(date_str, '%d/%m/%y').date()
                                else:
                                    date = datetime.strptime(date_str, '%d/%m/%Y').date()
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
                        if data:
                            if perfil=="carga":
                                verificar_repetidos = db.query(DatosMedidorConsumo)
                            else:
                                verificar_repetidos = db.query(DatosMedidorInstrumentacion)

                            existing_record = verificar_repetidos.filter_by(
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
                    if data:
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

# esta función guarda información de los medidores en la tabla 'medidores'
def evaluar_guardar_medidores_factor(lista_rutas):
    # creacion de la sesion para acceder a la base de datos
    db = SessionLocal()
    archivo_invalido = 0

    # se obtiene el nombre del archivo y su extensión
    archivo_cargado = lista_rutas[0]
    nombre_archivo = os.path.basename(archivo_cargado)
    extension_archivo = os.path.splitext(nombre_archivo)[1]
    
    # archivo seleccionado
    if len(lista_rutas)!=1 and extension_archivo!=".xlsx":
        archivo_invalido+=1
        pass
    else:
        # carga el archivo excel en un data frame de pandas
        try:
            df = pd.read_excel(lista_rutas[0], sheet_name='Ord. Fecha', header=None, skiprows=3, usecols=[2,3,5,6,7])
            #print(df)
            df.columns = ['SED', 'Fecha Instalación','N° medidor instalado', 'Marca', 'Factor']
        except Exception as e:
            print("Error al cargar el archivo Excel:", e)
            archivo_invalido += 1
            return archivo_invalido
        #print(df)

        # imprime los datos obtenidos del archivo Excel
        #print("Datos encontrados:")
        for index, row in df.iterrows():
            #print(row)
            # creando una instancia de medidores para cada fila
            # esta instancia será guardada en la base de datos
            # verificar si el medidor ya existe en la base de datos
            medidor_existente = db.query(Medidores).filter_by(id=row['N° medidor instalado']).first()
            # si el medidor ya existe en la base de datos
            if medidor_existente:
                # actualiza el medidor existente con los nuevos datos del archivo Excel en cada una de sus columnas
                medidor_existente.sed = row['SED']
                medidor_existente.fecha_instalacion = row['Fecha Instalación']
                medidor_existente.marca = row['Marca']
                medidor_existente.factor = row['Factor']
            else:
                # se crea una nueva instancia para un medidor
                medidor = Medidores(
                    # se añade el valor de cada columna en la presente fila
                    id=row['N° medidor instalado'],
                    sed=row['SED'],
                    fecha_instalacion=row['Fecha Instalación'],
                    marca=row['Marca'],
                    factor=row['Factor']
                )
                try:
                    # añade la instancia
                    db.add(medidor)
                except IntegrityError as e:
                    # en caso de que exista un error de integridad
                    print("Error al guardar el medidor:", e)
                    # se deshace la información y los objetos a guardar con la sesión
                    db.rollback()
                    archivo_invalido += 1
                else:
                    print("Medidor guardado exitosamente.")

        # guardar los cambios en la base de datos
        db.commit()

    return archivo_invalido