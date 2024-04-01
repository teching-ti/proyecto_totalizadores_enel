import tkinter as tk
from tkcalendar import Calendar

def generar_reportes():
    # Crear la ventana de periodo
    ventana_periodo = tk.Toplevel()
    ventana_periodo.title("Periodo")

    # Etiqueta y selector de fecha de inicio
    etiqueta_fecha_inicio = tk.Label(ventana_periodo, text="Fecha de inicio:")
    etiqueta_fecha_inicio.grid(row=0, column=0, padx=10, pady=5)
    seleccion_fecha_inicio = Calendar(ventana_periodo)
    seleccion_fecha_inicio.grid(row=0, column=1, padx=10, pady=5)

    # Etiqueta y selector de fecha de fin
    etiqueta_fecha_fin = tk.Label(ventana_periodo, text="Fecha de fin:")
    etiqueta_fecha_fin.grid(row=1, column=0, padx=10, pady=5)
    seleccion_fecha_fin = Calendar(ventana_periodo)
    seleccion_fecha_fin.grid(row=1, column=1, padx=10, pady=5)

    # Función para manejar el clic en el botón Aceptar
    def aceptar():
        fecha_inicio = seleccion_fecha_inicio.get_date()
        fecha_fin = seleccion_fecha_fin.get_date()
        print("Fecha de inicio:", fecha_inicio)
        print("Fecha de fin:", fecha_fin)
        ventana_periodo.destroy()

    # Botón Aceptar
    boton_aceptar = tk.Button(ventana_periodo, text="Aceptar", command=aceptar)
    boton_aceptar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
