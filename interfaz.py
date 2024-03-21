from flet import *
import flet as ft
import os
from time import sleep
from logica_guardar_datos import evaluar_guardar_archivos

def main(page: ft.Page):
    # datos de la ventana
    page.title = "Aplicativo para GGEE By TI"
    page.bgcolor = ft.colors.ON_SECONDARY_CONTAINER
    page.window_width = 1360
    page.window_height = 1000
    page.window_maximizable = False
    page.window_resizable = False
    # posicionammiento para donde debería de aparecer la ventana
    page.window_center()

    # funcionalidad para poder seleccionar los archivos
    def dialog_picker(e:FilePickerResultEvent):
        # aquí estamos guardando la ruta de los archivos seleccionados
        # de esta manera luego podremos enviar esta información de rutas para poder manipular estos archivos
        # se crea la variable como global, debido a que está dentro de una función, se guarda separado por comas y un salto de línea
        # variable para almacenar ruta de archivos
        global archivos_cargados
        archivos_cargados = (",\n".join(map(lambda f: f.path, e.files))) if e.files else "Se canceló la operación. No se ha seleccionado ningún archivo"

        # se crea una variable para obtener solo el nombre de los archivos
        archivos_cargados_nombres = ("\n".join(map(lambda f: f.name, e.files))) if e.files else "Se canceló la operación. No se ha seleccoinado ningún archivo."
        # se añaden las rutas de los archivos a la casilla de texto
        # se pretende cambiar esa casilla de texto por un scroll
        archivos_seleccionados_texto.value = archivos_cargados_nombres

        # ////**** Se pretende mostrar los nombres de los archivos en un mensaje de alerta que diga algo como 'archivos cargados y muestre el nombre de todos los archivos, si ha cometido un error solo vuelva a realizar otra selección antes de guardar'
        # modiifcación visual
        
        # en este apartado se actualiza la casilla de texto para mostrar la información que ahora posee
        archivos_seleccionados_texto.update()
    
    # esta variable es una casilla de texto en donde se mostará el nombre de los archivos
    archivos_seleccionados_texto = ft.Text(color=ft.colors.BLACK, selectable=True)

    # se muestra la ventana para poder seleccionar archivos
    pick_files_dialog = FilePicker(on_result=dialog_picker)
    page.overlay.append(pick_files_dialog)

    # método que envía la ruta de los archivos al código de procesar
    def enviar_rutas_archivos():
        try:
            # la variable archivos_cargados reemplaza el salto de línea guarda el resultado en una lista
            rutas = archivos_cargados.replace("\n", "")
            lista = rutas.split(",")
            # agregar el método que se encargue de enviar la lista de rutas al py que ejecutará la lógica
            evaluar_guardar_archivos(lista)
        except:
            print("Informar al usuario que primero debe seleccionar archivos")
        
    # creacion del boton para seleccionar y cargar los archivos con los que se realizará el proceso
    btnSeleccionar =  ElevatedButton("Seleccionar archivos", icon=ft.icons.UPLOAD_FILE, style=ft.ButtonStyle(
        color={
            ft.MaterialState.HOVERED: ft.colors.WHITE,
            ft.MaterialState.DEFAULT: ft.colors.BLACK,
        },
        bgcolor={
            ft.MaterialState.HOVERED: ft.colors.GREY,
            ft.MaterialState.DEFAULT: ft.colors.BLUE_50
            }),
            on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=True, allowed_extensions= ["prn", "csv"])
        )

    # creacion del boton para insertar la información de los datos cargados
    btnGuardarData = ElevatedButton("Guardar datos", icon=ft.icons.SAVE, style=ft.ButtonStyle(
        color={
            ft.MaterialState.HOVERED: ft.colors.WHITE,
            ft.MaterialState.DEFAULT: ft.colors.BLACK,
        },
        bgcolor={
            ft.MaterialState.HOVERED: ft.colors.GREY,
            ft.MaterialState.DEFAULT: ft.colors.BLUE_50
        }),
        on_click=lambda _: enviar_rutas_archivos()
        )

    #se añaden los elementos creados a la ventana
    page.add(

        ResponsiveRow(
            [ft.Container(
                btnSeleccionar,
                col={"sm": 3},
            ),
            ft.Container(
                btnGuardarData,
                col={"sm": 3},
            )], 
            alignment=MainAxisAlignment.CENTER
        ),

        ResponsiveRow(
            [
            ft.Container(
                archivos_seleccionados_texto,
            )]
        ),

    )
    
ft.app(target=main)