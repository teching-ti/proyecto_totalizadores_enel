from flet import *
import flet as ft
import os
from time import sleep
from logica_guardar_datos import evaluar_guardar_archivos
import datetime

# comentarios

def main(page: ft.Page):
    # datos de la ventana
    page.title = "Aplicativo para GGEE By TI"
    page.bgcolor = ft.colors.SECONDARY_CONTAINER
    page.window_width = 1350
    page.window_height = 1000
    page.window_maximizable = False
    page.window_resizable = False
    # posicionammiento para donde debería de aparecer la ventana
    page.window_center()

    '''PROBANDO DATE PICKER'''
    def change_date(e):
        print(f"Date picker changed, value is: ")
        #print(date_picker.value.date())
        primera_fecha = date_picker.value.date()
        

    def date_picker_dismissed(e):
        print(f"Date picker dismissed, value is {date_picker.value}")

    date_picker = ft.DatePicker(
        on_change=change_date,
        on_dismiss=date_picker_dismissed,
        first_date=datetime.datetime(2023, 10, 1),
        last_date=datetime.datetime(2050, 10, 1),
    )

    page.overlay.append(date_picker)

    date_button = ft.ElevatedButton(
        "Seleccionar Fecha",
        icon=ft.icons.CALENDAR_MONTH,
        on_click=lambda _: date_picker.pick_date(),
    )
    '''HASTA AQUI VA EL DATE PCIKER'''

    # funcionalidad para poder seleccionar los archivos
    def dialog_picker(e:FilePickerResultEvent):
        # aquí estamos guardando la ruta de los archivos seleccionados
        # de esta manera luego podremos enviar esta información de rutas para poder manipular estos archivos
        # se crea la variable como global, debido a que está dentro de una función, se guarda separado por comas y un salto de línea
        # variable para almacenar ruta de archivos
        global archivos_cargados
        archivos_cargados = (",\n".join(map(lambda f: f.path, e.files))) if e.files else "Debido a que no se seleccionó ningún archivo"

        # se crea una variable para obtener solo el nombre de los archivos
        archivos_cargados_nombres = ("\n".join(map(lambda f: f.name, e.files))) if e.files else "Se canceló la operación. No se ha seleccoinado ningún archivo."
        # se añaden las rutas de los archivos a la casilla de texto
        # se pretende cambiar esa casilla de texto por un scroll
        archivos_seleccionados_texto.value = archivos_cargados_nombres

        # ////**** Se pretende mostrar los nombres de los archivos en un mensaje de alerta que diga algo como 'archivos cargados y muestre el nombre de todos los archivos, si ha cometido un error solo vuelva a realizar otra selección antes de guardar'
        # modiifcación visual
        
        # en este apartado se actualiza la casilla de texto para mostrar la información que ahora posee
        '''En esta seccion se puede colocar una lista para mostrar todos los archivos cargados'''
        dialog_open_seleccionados()
    
    # esta variable es una casilla de texto en donde se mostará el nombre de los archivos
    archivos_seleccionados_texto = ft.Text(selectable=True)

    # se muestra la ventana para poder seleccionar archivos
    pick_files_dialog = FilePicker(on_result=dialog_picker)
    page.overlay.append(pick_files_dialog)

    # método que envía la ruta de los archivos al código de procesar
    def enviar_rutas_archivos():
        try:
            # la variable archivos_cargados reemplaza el salto de línea guarda el resultado en una lista
            rutas = archivos_cargados.replace("\n", "")
            lista = rutas.split(",")
            
            # la linea siguiente es una variable que contiene una funcion, esta se ejecutará y el resultado devuelto 'return, se guardará en esta variable'
            # entonces,a partir de aquí continúa la secuencia el archivo 'logica_guardar_datos'
            archivos_no_procesados = evaluar_guardar_archivos(lista)
            #print(archivos_no_procesados)
            ''' INCIA ALERT DIALOG (MODAL) PARA MOSTRAR INFORMACIÓN DE SI LOS ARCHIVOS FUERON PROCESADOS POR LA LÓGICA O NO'''
            # si el archivo logica, devuelve información 'osea la lista de archivos no permitidos con data', se ejecuta la siguiente condición
            if archivos_no_procesados:
                titulo = "Archivos inválidos"
                mensaje = "\n".join(archivos_no_procesados)
                icono = ft.Icon(name=ft.icons.WARNING_AMBER)
            else:
                titulo = "Todos los archivos fueron procesados con éxito"
                mensaje = "Todo bien."
                icono = ft.Icon(name=icons.CHECK_CIRCLE_OUTLINED)
                
            # mostrar la información en un alert dialog de flet, o buscar la manera
            # se establecen las propiedades del AlertDialog en base a las condiciones anteriores
            # alerta_archivos_procesador
            alerta_archivos_procesados = AlertDialog(
                title=Text(titulo),
                content=ft.Text(mensaje),
                icon = icono,
                on_dismiss=lambda event: True
            )

            def dialog_open():
                page.dialog = alerta_archivos_procesados
                alerta_archivos_procesados.open = True
                page.update()

            dialog_open()
            ''' TERMINA LA ALERTA '''
        except:
            print("Informar al usuario que primero debe seleccionar archivos")


    # método para enviar las fechas seleccionadas al archivo que realizará el cálculo y mostrará el gráfico
    '''
    -------
    '''
            
    # funcion para mostrar los archivos cargados en un alert
    alerta_archivos_seleccionados = AlertDialog(
        title=Text('Archivos cargados'),
        content=archivos_seleccionados_texto,
        icon = ft.Icon(name=ft.icons.WARNING_AMBER),
        on_dismiss=lambda event: True
    )

    def dialog_open_seleccionados():
        page.dialog = alerta_archivos_seleccionados
        alerta_archivos_seleccionados.open = True
        page.update()

    
        
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
            ft.MaterialState.DEFAULT: ft.colors.BLACK
        },
        bgcolor={
            ft.MaterialState.HOVERED: ft.colors.GREY,
            ft.MaterialState.DEFAULT: ft.colors.BLUE_50
        }),
        on_click=lambda _: enviar_rutas_archivos(),
        )

    #se añaden los elementos creados a la ventana
    page.add(
        Row(
            [ft.Container(
                btnSeleccionar,
                col={"sm": 2.5},
                margin=18,
            ),
             ft.VerticalDivider(width=9),
            ft.Container(
                btnGuardarData,
                col={"sm": 2.5},
                margin=18,
            ),
            #  ft.VerticalDivider(width=9),
            # ft.Container(
            #     Text("Aqui ira otro elemento\nservirá para mostrar los archivos seleccionados", color="black"),
            #     width=350,
            #     bgcolor=ft.colors.BLUE_50,
            #     margin=18,
            #     height=250,
            # )
            ], 
            alignment=MainAxisAlignment.CENTER,
            #spacing=0,
        ),

        Row(
            [
            ft.Container(
                width=350,
            ),
            ]
        ),
        Row(
            [
            ft.Container(
                date_button,
            ),
            ]
        )
    )
 
ft.app(target=main)