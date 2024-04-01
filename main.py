import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Label, Treeview
from PIL import Image, ImageTk
from logica_guardar_datos import evaluar_guardar_archivos

# Base de datos
from db import SessionLocal
from modelos import DatosMedidorConsumo

# Reportes
from ventana_periodo import generar_reportes

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

#def generar_reportes():
    # mostrando el id del medidor seleccionado
    # valores = []

    # indices_seleccionados = treeview_medidores.selection()
    # for indice in indices_seleccionados:
    #         medidor = treeview_medidores.item(indice, "text")
    #         valores.append(medidor)
    # # Mostrar los IDs de los medidores seleccionados
    # messagebox.showinfo("Medidores seleccionados", f"ID del medidor seleccionado: {', '.join(valores)}")


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
root.title("Aplicación de Ejemplo (Totalizadores)")
root.geometry("1360x600")
root.config(bg="white")
icono = tk.PhotoImage(file="./images/fav-icon-ti.png")
root.iconphoto(True, icono)

menu_frame = tk.Frame(root, bg="#2f3640", width=100)
menu_frame.pack(side="left", fill="y", expand=False)

menu_titulo = tk.Label(menu_frame, text="Menú", font=("Arial", 14), bg="#2f3640", fg="white")
menu_titulo.pack(pady=10)

icono1 = tk.PhotoImage(file="images/img1.png")
imagen1 = icono1

icono2 = tk.PhotoImage(file="images/img2.png")
imagen2 = icono2

icono3 = tk.PhotoImage(file="images/img3.png")
imagen3 = icono3

icono4 = tk.PhotoImage(file="images/img4.png")
imagen4 = icono4

boton_importar = tk.Button(menu_frame, text="   Importar   ", image=imagen1, compound=tk.LEFT, command=importar_lecturas, width=140)
boton_importar.pack(pady=25, padx=20)
boton_reportes = tk.Button(menu_frame, text="   Gen. Reportes   ", image=imagen2, compound=tk.LEFT, command=generar_reportes, width=140)
boton_reportes.pack(pady=25, padx=20)
boton_eliminar = tk.Button(menu_frame, text="   Eliminar   ", image=imagen3, compound=tk.LEFT, command=eliminar_datos, width=140)
boton_eliminar.pack(pady=25, padx=20)
boton_salir = tk.Button(menu_frame, text="   Salir   ", image=imagen4, compound=tk.LEFT ,command=salir, width=140)
boton_salir.pack(pady=25, padx=20)

datos_historicos_frame = tk.Frame(root, bg="#2f3640", padx=20, pady=20)
datos_historicos_frame.pack(side="left", fill="both", expand=True)

treeview_medidores = Treeview(datos_historicos_frame, columns=("Primer Registro", "Último Registro", "Huecos/Vacios"))
treeview_medidores.heading("#0", text="Medidor")
treeview_medidores.heading("#1", text="Primer Registro")
treeview_medidores.heading("#2", text="Último Registro")
treeview_medidores.heading("#3", text="Huecos/Vacios")
treeview_medidores.pack(expand=True, fill="both")

actualizar_lista_medidores()

root.mainloop()
