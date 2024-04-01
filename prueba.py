import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from logica_guardar_datos import evaluar_guardar_archivos

#base de datos
from db import SessionLocal
from modelos import DatosMedidorConsumo

def obtener_medidores():
    # Creamos una sesión de SQLAlchemy
    db = SessionLocal()
    try:
        # Consultamos todos los registros de la tabla datos_medidor_consumo
        medidores = db.query(DatosMedidorConsumo.meter_id).distinct().all()
        
        # Convertimos los resultados en una lista de IDs de medidores únicos
        ids_medidores = [medidor[0] for medidor in medidores]
        
        return ids_medidores
    finally:
        # Cerramos la sesión de SQLAlchemy
        db.close()

def importar_lecturas():
    # Abre una ventana para seleccionar los archivos
    tipos_archivos = [("Archivos CSV y PRN", "*.csv;*.prn")]

    archivos_seleccionados = filedialog.askopenfilenames(title="Seleccione archivos CSV o PRN", filetypes=tipos_archivos)

    if archivos_seleccionados:
        # Evalúa y guarda los archivos
        archivos_no_validos = evaluar_guardar_archivos(archivos_seleccionados)

        if archivos_no_validos:
            # Si hay archivos no válidos, muestra un mensaje con los nombres de los archivos no válidos
            mensaje = "Los siguientes archivos no son válidos:\n" + "\n".join(archivos_no_validos)
            messagebox.showwarning("Archivos no válidos", mensaje)
        else:
            # Si todos los archivos son válidos, muestra un mensaje de éxito
            messagebox.showinfo("Éxito", "Todos los archivos fueron importados correctamente.")

            # Actualizar la lista de IDs de medidores
            medidores = obtener_medidores()
            for medidor in medidores:
                checkbutton = tk.Checkbutton(datos_historicos_frame, text=medidor)
                checkbutton.pack(anchor="w")
    else:
        # Si no se seleccionaron archivos, muestra un mensaje de advertencia
        messagebox.showinfo("Mensaje", "No se seleccionaron archivos para importar.")

def generar_reportes():
    messagebox.showinfo("Generar Reportes", "Funcionalidad de Generar Reportes")

def eliminar_datos():
    messagebox.showinfo("Eliminar Datos", "Funcionalidad de Eliminar Datos")

def salir():
    root.destroy()

# Crear la ventana de tkinter
root = tk.Tk()

# Configuración de la ventana principal
root.title("Aplicación de Ejemplo (Totalizadores)")
root.geometry("1400x700")
root.config(bg="white")
icono = tk.PhotoImage(file="./images/fav-icon-ti.png")
root.iconphoto(True, icono)

# Configurar el menú vertical
menu_frame = tk.Frame(root, bg="#2f3640", width=100)  # Menú en el lado izquierdo
menu_frame.pack(side="left", fill="y", expand=False)

# Título del menú
menu_titulo = tk.Label(menu_frame, text="Menú", font=("Arial", 14), bg="#2f3640", fg="white")
menu_titulo.pack(pady=10)

# icono para boton
#icono1
icono1 = tk.PhotoImage(file="images/img1.png")
imagen1 = icono1

#icono2
icono2 = tk.PhotoImage(file="images/img2.png")
imagen2 = icono2

#icono3
icono3 = tk.PhotoImage(file="images/img3.png")
imagen3 = icono3

#icono4
icono4 = tk.PhotoImage(file="images/img4.png")
imagen4 = icono4

# Botones del menú
boton_importar = tk.Button(menu_frame, text="   Importar   ", image=imagen1, compound=tk.LEFT, command=importar_lecturas, width=140)
boton_importar.pack(pady=25, padx=20)
boton_reportes = tk.Button(menu_frame, text="   Gen. Reportes   ", image=imagen2, compound=tk.LEFT, command=generar_reportes, width=140)
boton_reportes.pack(pady=25, padx=20)
boton_eliminar = tk.Button(menu_frame, text="   Eliminar   ", image=imagen3, compound=tk.LEFT, command=eliminar_datos, width=140)
boton_eliminar.pack(pady=25, padx=20)
boton_salir = tk.Button(menu_frame, text="   Salir   ", image=imagen4, compound=tk.LEFT ,command=salir, width=140)
boton_salir.pack(pady=25, padx=20)

# Marco para mostrar la lista de IDs de medidores y el widget de selección
datos_historicos_frame = tk.Frame(root, bg="#2f3640", padx=20, pady=20)
datos_historicos_frame.pack(side="left", fill="both", expand=True)

# Mantener la ventana abierta
root.mainloop()