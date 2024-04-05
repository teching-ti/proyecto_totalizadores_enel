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

# Base de datos
from db import SessionLocal
from modelos import DatosMedidorConsumo

# Reportes
# primer grafico y data
from reporte_consumos import obtener_consumo_por_medidor_y_rango, generar_grafico_consumo_por_horas

def obtener_medidores_info():
    db = SessionLocal()
    try:
        medidores_info = []
        for medidor in db.query(DatosMedidorConsumo.meter_id).distinct().all():
            primer_registro = db.query(DatosMedidorConsumo.date).filter_by(meter_id=medidor[0]).order_by(DatosMedidorConsumo.date).first()
            ultimo_registro = db.query(DatosMedidorConsumo.date).filter_by(meter_id=medidor[0]).order_by(DatosMedidorConsumo.date.desc()).first()
            huecos = db.query(DatosMedidorConsumo).filter(DatosMedidorConsumo.meter_id == medidor[0], DatosMedidorConsumo.kwh_del.is_(None)).count()
            medidores_info.append((medidor[0], primer_registro[0], ultimo_registro[0], huecos))
        return medidores_info
    finally:
        db.close()

def eliminar_registros_medidor(medidor):
    db = SessionLocal()
    try:
        db.query(DatosMedidorConsumo).filter_by(meter_id=medidor).delete()
        db.commit()
        messagebox.showinfo("Eliminación exitosa", f"Los datos del medidor {medidor} han sido eliminados.")
    except Exception as e:
        db.rollback()
        messagebox.showerror("Error", f"No se pudo eliminar los datos del medidor {medidor}: {str(e)}")
    finally:
        db.close()

def importar_lecturas():
    tipos_archivos = [("Archivos CSV y PRN", "*.csv;*.prn")]
    archivos_seleccionados = filedialog.askopenfilenames(title="Seleccione archivos CSV o PRN", filetypes=tipos_archivos)
    if archivos_seleccionados:
        archivos_no_validos = evaluar_guardar_archivos(archivos_seleccionados)
        if archivos_no_validos:
            mensaje = "Los siguientes archivos no son válidos:\n" + "\n".join(archivos_no_validos)
            messagebox.showwarning("Archivos no válidos", mensaje)
        else:
            messagebox.showinfo("Éxito", "Todos los archivos fueron importados correctamente.")
            actualizar_lista_medidores()
    else:
        messagebox.showinfo("Mensaje", "No se seleccionaron archivos para importar.")

def generar_reportes_one():
    # se puede crear una lista para guardar a todos los medidores
    lista_medidores = []
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

def generar_reportes(fecha_inicio, fecha_fin):
    # Obtiene los identificadores de los medidores seleccionados
    medidores_seleccionados = [treeview_medidores.item(item, "text") for item in treeview_medidores.selection()]
    #print("DATA A MODO DE REPORTE")
    datos_obtenidos = []
    for medidor_id in medidores_seleccionados:
        # Llamada a la función en reporte_consumos para obtener los datos de consumo en el rango de fechas especificado
        datos_consumo = obtener_consumo_por_medidor_y_rango(fecha_inicio, fecha_fin, medidor_id)
        # Llamada a la función en reporte_consumos para generar el gráfico con los datos de consumo obtenidos
        #print(datos_consumo)
        datos_obtenidos.append(datos_consumo)

    for datos in datos_obtenidos:
            # Insertar cada conjunto de datos como una nueva fila en el treeview_reportes
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

def generar_reportes_periodo():
    fecha_inicio_str = seleccion_fecha_inicio.get_date()
    fecha_fin_str = seleccion_fecha_fin.get_date()

    # Convertir las cadenas a objetos de fecha
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%m/%d/%y").date()
    fecha_fin = datetime.strptime(fecha_fin_str, "%m/%d/%y").date()

    ventana_periodo.destroy()
    generar_reportes(fecha_inicio, fecha_fin)

def abrir_ventana_periodo():
    global ventana_periodo
    global seleccion_fecha_inicio
    global seleccion_fecha_fin
    ventana_periodo = tk.Toplevel()
    ventana_periodo.title("Periodo")
    
    # Label y selección de fecha de inicio
    label_fecha_inicio = ttk.Label(ventana_periodo, text="Fecha de inicio:")
    label_fecha_inicio.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    seleccion_fecha_inicio = Calendar(ventana_periodo)
    seleccion_fecha_inicio.grid(row=0, column=1, padx=5, pady=5)

    # Label y selección de fecha de fin
    label_fecha_fin = ttk.Label(ventana_periodo, text="Fecha de fin:")
    label_fecha_fin.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    seleccion_fecha_fin = Calendar(ventana_periodo)
    seleccion_fecha_fin.grid(row=1, column=1, padx=5, pady=5)

    # Botón de aceptar
    boton_aceptar = ttk.Button(ventana_periodo, text="Aceptar", command=generar_reportes_periodo)
    boton_aceptar.grid(row=2, column=0, columnspan=2, pady=10)

    ventana_periodo.mainloop()

def eliminar_datos():
    indices_seleccionados = treeview_medidores.selection()
    if not indices_seleccionados:
        messagebox.showwarning("Selección vacía", "Por favor, seleccione al menos un medidor para eliminar.")
        return
    respuesta = messagebox.askquestion("Confirmar Eliminación", "¿Está seguro de que desea eliminar el registro seleccionado?")
    if respuesta == "yes":
        for indice in indices_seleccionados:
            medidor = treeview_medidores.item(indice, "text")
            eliminar_registros_medidor(medidor)
        actualizar_lista_medidores()

def salir():
    root.destroy()

def actualizar_lista_medidores():
    treeview_medidores.delete(*treeview_medidores.get_children())
    medidores_info = obtener_medidores_info()
    for medidor_info in medidores_info:
        medidor = medidor_info[0]
        primer_registro = medidor_info[1]
        ultimo_registro = medidor_info[2]
        huecos = medidor_info[3]
        treeview_medidores.insert("", "end", text=medidor, values=(primer_registro, ultimo_registro, huecos))

root = tk.Tk()
root.title("Aplicativo para la campaña de totalizadores")
root.geometry("1450x800")
root.config(bg="white")
icono = tk.PhotoImage(file="./images/fav-icon-ti.png")
root.iconphoto(True, icono)

menu_frame = tk.Frame(root, bg="#2f3640", width=100)
menu_frame.pack(side="left", fill="y", expand=False)

logo = tk.PhotoImage(file="./images/logo_teching.png")

menu_titulo = tk.Label(menu_frame, image=logo ,compound=tk.LEFT, font=("Arial", 14), bg="#2f3640", fg="white")
menu_titulo.pack(pady=35)

icono1 = tk.PhotoImage(file="images/img1.png")
imagen1 = icono1

icono2 = tk.PhotoImage(file="images/img2.png")
imagen2 = icono2

icono3 = tk.PhotoImage(file="images/img3.png")
imagen3 = icono3

icono4 = tk.PhotoImage(file="images/img4.png")
imagen4 = icono4

boton_importar = tk.Button(menu_frame, text="   Importar   ", image=imagen1, compound=tk.LEFT, command=importar_lecturas, width=140, cursor="hand2")
boton_importar.pack(pady=25, padx=20)
boton_reportes = tk.Button(menu_frame, text="   Gen. Reportes   ", image=imagen2, compound=tk.LEFT, command=generar_reportes_one, width=140, cursor="hand2")
boton_reportes.pack(pady=25, padx=20)
boton_eliminar = tk.Button(menu_frame, text="   Eliminar   ", image=imagen3, compound=tk.LEFT, command=eliminar_datos, width=140, cursor="hand2")
boton_eliminar.pack(pady=25, padx=20)
boton_salir = tk.Button(menu_frame, text="   Salir   ", image=imagen4, compound=tk.LEFT ,command=salir, width=140, cursor="hand2")
boton_salir.pack(pady=25, padx=20)

# Crear el Notebook
'''TK NOTEBOOK - PANEL DE PESTAÑAS EN DONDE ESTARÁN ALOJADAS LAS PESTAÑAS: ("DATOS HISTÓRICOS", "REPORTES")'''
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Frame para los datos históricos
datos_historicos_frame = tk.Frame(notebook, bg="#2f3640", padx=20, pady=20)
notebook.add(datos_historicos_frame, text="Datos Históricos")

# Frame para los reportes
reportes_frame = tk.Frame(notebook, bg="#2f3640", padx=20, pady=20)
notebook.add(reportes_frame, text="Reportes")

''' /*/*/*/*/* INICIA CONTENIDO DE DATOS HISTORICOS '''
datos_historicos_title = tk.Label(datos_historicos_frame, text="Datos Históricos - Perfiles de Carga", bg="#2f3640", fg="white", font=("Arial", 12))
datos_historicos_title.pack(side="top", fill="x")
datos_historicos_title.configure(anchor="w") 

treeview_medidores = Treeview(datos_historicos_frame, columns=("Primer Registro", "Último Registro", "Huecos/Vacios"))
treeview_medidores.heading("#0", text="Medidor")
treeview_medidores.heading("#1", text="Primer Registro")
treeview_medidores.heading("#2", text="Último Registro")
treeview_medidores.heading("#3", text="Huecos/Vacios")
treeview_medidores.pack(expand=True, fill="both")
''' /*/*/*/*/* TERMINA CONTENIDO DE DATOS HISTORICOS '''

''' /*/*/*/*/* INICIA CONTENIDO PARA REPORTES ESTADÍSTICOS '''
reportes_estadisticos_title = tk.Label(reportes_frame, bg="#2f3640", fg="white", font=("Arial", 12))
reportes_estadisticos_title.pack(side="top", fill="x")
reportes_estadisticos_title.configure(anchor="w", text="Reportes - Perfiles de Carga")


# Agrega un botón a la pestaña de reportes_frame
boton_generar_documento = ttk.Button(reportes_estadisticos_title, text="G. Doc", cursor="hand2")
boton_generar_documento.pack(side="right")

def sort_column(treeview, col, reverse):
    data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
    data.sort(reverse=reverse)

    for index, (val, child) in enumerate(data):
        treeview.move(child, '', index)

    treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))

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
treeview_reportes.heading("col7", text="Energía - Mes")
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