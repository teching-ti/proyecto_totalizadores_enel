import flet as ft

def main(page: ft.Page):
    page.title = "Probando Interfaz"
    page.window_width = 1650
    page.window_height = 1000
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_maximizable = False
    page.window_resizable = False
    page.window_center()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        # extended=True,
        min_width=100,
        min_extended_width=400,
        leading=ft.FloatingActionButton(icon=ft.icons.ELECTRIC_BOLT, text="Menu"),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.CLOUD_UPLOAD_OUTLINED, selected_icon=ft.icons.CLOUD_UPLOAD_ROUNDED, label="Importar Lecturas",
                padding= 60
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.INSERT_DRIVE_FILE_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.INSERT_DRIVE_FILE_ROUNDED),
                label="Gen. Reportes",
                padding= 60
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.DELETE_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.DELETE_ROUNDED),
                label_content=ft.Text("Eliminar"),
                padding= 60
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.DOOR_FRONT_DOOR_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.DOOR_FRONT_DOOR_ROUNDED),
                label_content=ft.Text("Salir"),
                padding= 60
            ),
        ],
        on_change=lambda e: print("Selected destination:", e.control.selected_index),
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Column([ ft.Text("hOLA!")], alignment=ft.MainAxisAlignment.START, expand=True),
            ],
            expand=True,
        )
    )

ft.app(target=main)