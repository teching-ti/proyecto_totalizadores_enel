import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Label, Treeview
from tkinter import ttk
from tkcalendar import Calendar
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from logica_guardar_datos import evaluar_guardar_archivos
import datetime
from datetime import datetime

import openpyxl
# Base de datos
from db import SessionLocal
from modelos import DatosMedidorConsumo

# Reportes
# primer grafico y data
from reporte_consumos import obtener_consumo_por_medidor_y_rango, generar_grafico_consumo_por_horas

# función para obtener información específica de los medidores, esta información serpa visible en la pestaña principal "Datos histróricos"
def obtener_medidores_info():
    # se accede a la sesión de la base de datos
    db = SessionLocal()
    try:
        # lista que cargará la data de los medidores según la base de dato
        medidores_info = []
        for medidor in db.query(DatosMedidorConsumo.meter_id).distinct().all():
            primer_registro = db.query(DatosMedidorConsumo.date).filter_by(meter_id=medidor[0]).order_by(DatosMedidorConsumo.date).first()
            ultimo_registro = db.query(DatosMedidorConsumo.date).filter_by(meter_id=medidor[0]).order_by(DatosMedidorConsumo.date.desc()).first()
            huecos = db.query(DatosMedidorConsumo).filter(DatosMedidorConsumo.meter_id == medidor[0], DatosMedidorConsumo.kwh_del.is_(None)).count()
            medidores_info.append((medidor[0], primer_registro[0], ultimo_registro[0], huecos))
        return medidores_info
    finally:
        db.close()

# función para eliminar los registros del medidor, interactuando con la interfaz principal del proyecto
def eliminar_registros_medidor(medidor):
    # se accede a la sesión de la base de datos
    db = SessionLocal()
    try:
        # consulta para eliminar el medidor o los medidores seleccionados
        db.query(DatosMedidorConsumo).filter_by(meter_id=medidor).delete()
        db.commit()
        messagebox.showinfo("Eliminación exitosa", f"Los datos del medidor {medidor} han sido eliminados.")
    except Exception as e:
        # se deshace la eliminación
        db.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar los datos del medidor {medidor}: {str(e)}")
    finally:
        db.close()

# función para importa datos
def importar_lecturas():
    # tipos de archivos permitidos
    tipos_archivos = [("Archivos CSV y PRN", "*.csv;*.prn")]
    # ventana de selección
    archivos_seleccionados = filedialog.askopenfilenames(title="Seleccione archivos CSV o PRN", filetypes=tipos_archivos)
    if archivos_seleccionados:
        # se ejecuta la función 'evaluar_guardar_archivos' dentro de una variable, la función creada en el archivo 'logica_guardar_datos.py' devuelve un una lista de nombres
        # esta lista de nombres estará guardada en la variable 'archivos_no_validos'
        archivos_no_validos = evaluar_guardar_archivos(archivos_seleccionados)
        
        # si existen datos en esta variable, se mostrará el nombre de estos archivos en un mensaje
        if archivos_no_validos:
            mensaje = "Los siguientes archivos no son válidos:\n" + "\n".join(archivos_no_validos)
            messagebox.showwarning("Archivos no válidos", mensaje)
        else:
        # si la lista esta vacía por no existir archivos inválidos se mostrará un mensaje de confirmación
            messagebox.showinfo("Éxito", "Todos los archivos fueron importados correctamente.")
            # se ejecuta la siguiente función que refresca la información mostrada en la interfaz
            actualizar_lista_medidores()
    else:
        messagebox.showinfo("Mensaje", "No se seleccionaron archivos para importar.")

# primera funcion para generar reportes
def generar_reportes_one():
    
    if not treeview_medidores.selection():
        messagebox.showwarning("Medidor no seleccionado", "Por favor, seleccione un medidor antes de generar el reporte.")
        return
    else:
        '''esta seccion sirve para obtener una lista con los medidores seleccionados y en la funcion de (generar_reportes) ya no se enviaría un id sino una lista de id'''
        #for item in treeview_medidores.selection():
        #    medidor_id = treeview_medidores.item(item, "text")
        #    lista_medidores.append(medidor_id)
        abrir_ventana_periodo()
    #print(lista_medidores)

# se abre la ventana para seleccionar periodo. (para que esta ventana aparezca, primero se debe de haber seleccionado uno o varios medidores)
def abrir_ventana_periodo():
    global ventana_periodo
    global seleccion_fecha_inicio
    global seleccion_fecha_fin
    ventana_periodo = tk.Toplevel()
    ventana_periodo.title("Periodo")

    ventana_periodo.resizable(0,0)
    
    # label y selección de fecha de inicio
    label_fecha_inicio = ttk.Label(ventana_periodo, text="Fecha de inicio:")
    label_fecha_inicio.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    seleccion_fecha_inicio = Calendar(ventana_periodo)
    seleccion_fecha_inicio.grid(row=0, column=1, padx=5, pady=5)

    # label y selección de fecha de fin
    label_fecha_fin = ttk.Label(ventana_periodo, text="Fecha de fin:")
    label_fecha_fin.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    seleccion_fecha_fin = Calendar(ventana_periodo)
    seleccion_fecha_fin.grid(row=1, column=1, padx=5, pady=5)

    # Botón de aceptar generar el reporte
    boton_aceptar = ttk.Button(ventana_periodo, text="Aceptar", command=generar_reportes_periodo)
    boton_aceptar.grid(row=2, column=0, columnspan=2, pady=10)

    ventana_periodo.mainloop()

# función que toma las fechas para generar el reporte
def generar_reportes_periodo():
    # fechas
    fecha_inicio_str = seleccion_fecha_inicio.get_date()
    fecha_fin_str = seleccion_fecha_fin.get_date()

    # Convertir las cadenas a objetos de fecha
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%m/%d/%y").date()
    fecha_fin = datetime.strptime(fecha_fin_str, "%m/%d/%y").date()
    # se cierra la nueva ventana tras haber seleccionado las fechas de manera exitosa
    ventana_periodo.destroy()
    # se ejecuta la última función, se pasan las fechas como argmentos

    generar_reportes(fecha_inicio, fecha_fin)

    ''' Luego de haber generado los reportes en la interfaz, esta sección mostrará en un mensaje de alerta el id de los medidores que no tengan registros en todas las fechas
    seleccionadas; sin embargo de la misma manera muestra el reporte ya que al menos cuenta con data en los días iniciales'''
    id_medidores_fechas_excedentes = ""
    # con esta condición se evalúa si existe una cantidad de datos en el arreglo que contiene a los medidores cuyas de selección se exceden a las de registro
    if(len(datos_medidores_fechas)>=1):
        for dato_fecha in datos_medidores_fechas:
            id_medidores_fechas_excedentes+= f" - {dato_fecha} "

        messagebox.showinfo("Medidores sin registros en el rango de fechas seleccionadas", id_medidores_fechas_excedentes)

# se crea una variable global para luego poder usar la información que devuelva la función 'generar_reportes'
datos_obtenidos_globales = []

# se crea esta variable global, TENDRÁ LOS MEDIDORES CUYAS FECHAS DE SOLICITUD A LAS FECHAS DE REGISTRO
datos_medidores_fechas = ""

# función generar reportes, usando las fechas como arugmentos para otra función de se encuentra en 'reporte_cosumos'
def generar_reportes(fecha_inicio, fecha_fin):

    global datos_obtenidos_globales
    global datos_medidores_fechas

    # obtiene los identificadores de los medidores seleccionados
    medidores_seleccionados = [treeview_medidores.item(item, "text") for item in treeview_medidores.selection()]
    #print("DATA A MODO DE REPORTE")
    datos_obtenidos = []
    
    # por cada medidor seleccionado se obtiene su id de la lista para poder hacer uso de la función 'obtener_consumo_por_medidor_y_rango'
    # función que se encuentra en el archivo 'reporte_consumos.py'
    for medidor_id in medidores_seleccionados:
        # llamada a la función en reporte_consumos para obtener los datos de consumo en el rango de fechas especificado
        datos_consumo = obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)
        #print(datos_consumo)
        # se agrega en la lista todas listas devuelvas al ejecutar la función en el archivo de reporte
        datos_obtenidos.append(datos_consumo)

    #print(datos_obtenidos)

    # iterando la lista de datos
    try:
        for datos in datos_obtenidos:
            # se inserta cada conjunto de datos como una nueva fila en el treeview_reportes
            medidor = datos[0]
            dia = datos[1]
            mes = datos[2]
            cant_v = datos[3]
            desde = datos[4]
            hasta = datos[5]
            acum = datos[6]
            ener_mes = datos[7]
            hora = datos[8]
            tipo = datos[9]
            treeview_reportes.insert("", "end", text=medidor, values=(dia, mes, cant_v, desde, hasta, acum, ener_mes, hora, tipo))
                
        datos_medidores_fechas = (datos_obtenidos[-1][-1])
            # se guarda en la variable global la lista de datos obtenidos
        datos_obtenidos_globales = datos_obtenidos
    except:
        messagebox.showwarning("Aviso", "No se pudo completar la operación, inténtelo nuevamente y revise los rangos de fecha seleccionados")


    '''se desactiva de momento la presentación del gráfico'''
        # for widget in reportes_frame.winfo_children():
        #     widget.destroy()
        
        # Insertar los datos en el treeview
        # for hora, consumo in datos_consumo:
        #     treeview_reportes.insert("", "end", text=hora, values=(consumo,))

    # fig es lo que te retorna la funcion de generar_grafico_consumo_por_horas, se usaría para mostrar el gráfico en algún frame
    # fig = generar_grafico_consumo_por_horas(datos_consumo)

    # if fig!= None:
    #     canvas = FigureCanvasTkAgg(fig, master=reportes_frame)
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)
    # else:
    #     messagebox.showinfo("Mensaje", "Las fechas seleccionadas no existen en los registros")

# función para verificar si debe generarse el excel
def verificar_y_generar_excel():
    # revisa si existe contenido en el treeview_reportes
    if treeview_reportes.get_children():
        generar_excel()
    else:
        messagebox.showwarning("Sin datos", "No hay datos para generar el archivo Excel.")

# función para crear el excel con la data
def generar_excel():
    # uso de la variable global declarada anteriormente
    global datos_obtenidos_globales
    #print(datos_obtenidos_globales)
    # se crear un nuevo libro de Excel vacío

    workbook = openpyxl.Workbook()
    # obtiene la hoja activa del libro 'por defecto es la primera'
    sheet = workbook.active
    # le da título a la hoja activa
    sheet.title = "Reporte"

    # escribe los siguientes encabezados en la primera fila
    headers = ["Medidor", "Dias", "Mes", "Cant. Vacíos", "Desde", "Hasta", "Acumulado", "Energía - Mes", "Hora max.Demanda", "Tipo de Consumo"]

    # recorre la lista de headers
    for col, header in enumerate(headers, start=1):
        # con la finalidad de escribir los encabezados, empieza en la primera fila
        sheet.cell(row=1, column=col, value=header)

    # recorre los datos de la lista datos_obtenidos_globales, que contiene los datos recibidos
    for row, datos in enumerate(datos_obtenidos_globales, start=2):
        # Si hay datos y la longitud de la lista es mayor que 1
        if datos and len(datos) > 1:
            # se recorre cada elemento independiente de la lista datos
            for col, dato in enumerate(datos[:-1], start=1):  # Excluye el último elemento
                sheet.cell(row=row, column=col, value=dato)

    # se guardar el archivo Excel
    # se pregunta por el nombre del archivo y su ubicación
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")])
    if filename:
        # si existe un nombre asignado al archivo se guarda
        workbook.save(filename)
        # se muestra mensaje de confirmación
        messagebox.showinfo("Éxito", f"Archivo Excel guardado en {filename}")

# método para eliminar datos de los registros
# se puede eliminar uno o más medidores
def eliminar_datos():
    # guarda en una variable los elementos seleccionados
    indices_seleccionados = treeview_medidores.selection()
    # se valida que existan elemenetos seleccionados
    if not indices_seleccionados:
        messagebox.showwarning("Selección vacía", "Por favor, seleccione al menos un medidor para eliminar.")
        return
    # mensaje de confirmación para el usuario
    respuesta = messagebox.askquestion("Confirmar Eliminación", "¿Está seguro de que desea eliminar el registro seleccionado?")
    if respuesta == "yes":
        # se recorre la lista de elementos seleccionados
        for indice in indices_seleccionados:
            # se selecciona el valor del elemento seleccionado
            medidor = treeview_medidores.item(indice, "text")
            # se ejecuta la función con todos los valores extraídos de la lista
            eliminar_registros_medidor(medidor)
        # se ejecuta la función de actualizar para refrescar el frame
        actualizar_lista_medidores()

# cerrar el aplicativo
def salir():
    root.destroy()

# modifica el treeview y refresca el elemento
def actualizar_lista_medidores():
    # elimina todos los hijos del treeview
    treeview_medidores.delete(*treeview_medidores.get_children())
    # ejecuta la función para obtener datos
    medidores_info = obtener_medidores_info()
    # recorre la información obtenida
    for medidor_info in medidores_info:
        medidor = medidor_info[0]
        primer_registro = medidor_info[1]
        ultimo_registro = medidor_info[2]
        huecos = medidor_info[3]
        # inserta la información en el treeview
        treeview_medidores.insert("", "end", text=medidor, values=(primer_registro, ultimo_registro, huecos))

'''ventana del aplicativo'''
root = tk.Tk()
root.title("Aplicativo para la campaña de totalizadores")
root.geometry("1450x800")
root.config(bg="white")
icono = tk.PhotoImage(file="./images/fav-icon-ti.png")
root.iconphoto(True, icono)

'''Inicia Menu'''
# menu lateral
menu_frame = tk.Frame(root, bg="#2f3640", width=100)
menu_frame.pack(side="left", fill="y", expand=False)

# imagen del logo de teching
logo = tk.PhotoImage(file="./images/logo_teching.png")

# se carga la iamgen del logo en un label
menu_titulo = tk.Label(menu_frame, image=logo ,compound=tk.LEFT, font=("Arial", 14), bg="#2f3640", fg="white")
menu_titulo.pack(pady=35)

# se agrega un combobox para poder seleccionar con que tipo de perfil desea interactuar el usuario
combo = ttk.Combobox(
    menu_frame,
    state="readonly",
    values=["Perfiles de Carga", "Perfiles de Instrumentación"],
    width=26
)

combo.set("Perfiles de Carga")
combo.pack(pady=25, padx=20)

# se cargan los íconos para los botones
icono1 = tk.PhotoImage(file="images/img1.png")
imagen1 = icono1

icono2 = tk.PhotoImage(file="images/img2.png")
imagen2 = icono2

icono3 = tk.PhotoImage(file="images/img3.png")
imagen3 = icono3

icono4 = tk.PhotoImage(file="images/img4.png")
imagen4 = icono4

# se crean los botones y se coloca su respectivo texto e íconos
boton_importar = tk.Button(menu_frame, text="   Importar   ", image=imagen1, compound=tk.LEFT, command=importar_lecturas, width=140, cursor="hand2")
boton_importar.pack(pady=25, padx=20)
boton_reportes = tk.Button(menu_frame, text="   Gen. Reportes   ", image=imagen2, compound=tk.LEFT, command=generar_reportes_one, width=140, cursor="hand2")
boton_reportes.pack(pady=25, padx=20)
boton_eliminar = tk.Button(menu_frame, text="   Eliminar   ", image=imagen3, compound=tk.LEFT, command=eliminar_datos, width=140, cursor="hand2")
boton_eliminar.pack(pady=25, padx=20)
boton_salir = tk.Button(menu_frame, text="   Salir   ", image=imagen4, compound=tk.LEFT ,command=salir, width=140, cursor="hand2")
boton_salir.pack(pady=25, padx=20)

'''Finaliza Menu'''

# Crear el Notebook
'''TK NOTEBOOK - PANEL DE PESTAÑAS EN DONDE ESTARÁN ALOJADAS LAS PESTAÑAS: ("DATOS HISTÓRICOS", "REPORTES")'''
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# frame para los datos históricos
datos_historicos_frame = tk.Frame(notebook, bg="#2f3640", padx=20, pady=20)
notebook.add(datos_historicos_frame, text="Datos Históricos")

# frame para los reportes
reportes_frame = tk.Frame(notebook, bg="#2f3640", padx=20, pady=20)
notebook.add(reportes_frame, text="Reportes")

''' /*/*/*/*/* INICIA CONTENIDO DE DATOS HISTORICOS '''
# se asigna un titulo al frame de datos historicos
datos_historicos_title = tk.Label(datos_historicos_frame, text="Datos Históricos - Perfiles de Carga", bg="#2f3640", fg="white", font=("Arial", 12))
datos_historicos_title.pack(side="top", fill="x")
datos_historicos_title.configure(anchor="w") 

#se crea el treeview que mostrará información sobre los medidores
treeview_medidores = Treeview(datos_historicos_frame, columns=("Primer Registro", "Último Registro", "Huecos/Vacios"))
treeview_medidores.heading("#0", text="Medidor")
treeview_medidores.heading("#1", text="Primer Registro")
treeview_medidores.heading("#2", text="Último Registro")
treeview_medidores.heading("#3", text="Huecos/Vacios")
treeview_medidores.pack(expand=True, fill="both")
''' /*/*/*/*/* TERMINA CONTENIDO DE DATOS HISTORICOS '''

''' /*/*/*/*/* INICIA CONTENIDO PARA REPORTES ESTADÍSTICOS '''
# se asigna un titulo al frame de reportes estadísticos
reportes_estadisticos_title = tk.Label(reportes_frame, bg="#2f3640", fg="white", font=("Arial", 12))
reportes_estadisticos_title.pack(side="top", fill="x")
reportes_estadisticos_title.configure(anchor="w", text="Reportes - Perfiles de Carga")

# agrega un botón a la pestaña de reportes_frame
# este botón servirá para generar los reportes en excel haciendo uso de los datos obtenidos
boton_generar_documento = ttk.Button(reportes_estadisticos_title, text="G. Doc", cursor="hand2", command=verificar_y_generar_excel)
boton_generar_documento.pack(side="right")

# función que servirá para ordenar la información del treeview en la pestaña de reportes
def sort_column(treeview, col, reverse):
    # obtiene los datos y convertirlos a números si es posible, para luego poder ordenarlos de mayor a menor haciendo clic en los encabezados
    data = []
    for child in treeview.get_children(''):
        val = treeview.set(child, col)
        try:
            val = float(val)
        except ValueError:
            pass  # si no se puede convertir a número, lo deja como está
        data.append((val, child))
    
    # ordena los datos
    data.sort(reverse=reverse)

    # mueve los ítems en el Treeview a sus nuevas posiciones según el ordenamiento
    for index, (val, child) in enumerate(data):
        treeview.move(child, '', index)

    # configura el encabezado de la columna para invertir el orden al hacer clic
    treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))

# inserción de información
treeview_reportes = ttk.Treeview(reportes_frame, columns=("col1", "col2", "col3", "col4", "col5", "col6", "col7", "col8", "col9"))
treeview_reportes.column("#0", width=50)
treeview_reportes.column("col1", width=50)
treeview_reportes.column("col2", width=50)
treeview_reportes.column("col3", width=50)
treeview_reportes.column("col4", width=50)
treeview_reportes.column("col5", width=50)
treeview_reportes.column("col6", width=50)
treeview_reportes.column("col7", width=50)
treeview_reportes.column("col8", width=50)
treeview_reportes.column("col9", width=50)

treeview_reportes.heading("#0", text="Medidor")
treeview_reportes.heading("col1", text="Dias")
treeview_reportes.heading("col2", text="Mes")
treeview_reportes.heading("col3", text="Cant. Vacíos", command=lambda: sort_column(treeview_reportes, "col3", False))
treeview_reportes.heading("col4", text="Desde")
treeview_reportes.heading("col5", text="Hasta")
treeview_reportes.heading("col6", text="Acumulado", command=lambda: sort_column(treeview_reportes, "col6", False))
treeview_reportes.heading("col7", text="Energía - Mes", command=lambda: sort_column(treeview_reportes, "col7", False))
treeview_reportes.heading("col8", text="Hora max.Demanda", command=lambda: sort_column(treeview_reportes, "col8", False))
treeview_reportes.heading("col9", text="Tipo de Consumo")

treeview_reportes.pack(expand=True, fill="both")

''' /*/*/*/*/* TERMINA CONTENIDO PARA REPORTES ESTADÍSTICOS '''

# Esta función sirve para refrescar la lista de medidores mostrados en el frame de datos históricos
actualizar_lista_medidores()

notebook.pack(expand=True, fill="both")
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Aplicación interrumpida por el usuario.")
finally:
    root.destroy()