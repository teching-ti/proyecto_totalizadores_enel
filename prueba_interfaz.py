import flet as ft

def main(page: ft.Page):

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
                icon=ft.icons.CLOUD_UPLOAD_OUTLINED, selected_icon=ft.icons.CLOUD_UPLOAD_ROUNDED, label="Importar Lecturas"
            ),
            ft.Divider(),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.INSERT_DRIVE_FILE_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.INSERT_DRIVE_FILE_ROUNDED),
                label="Gen. Reportes",
            ),
            ft.Divider(),
            ft.NavigationRailDestination(
                icon=ft.icons.DELETE_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.DELETE_ROUNDED),
                label_content=ft.Text("Eliminar"),
            ),
            ft.Divider(),
            ft.NavigationRailDestination(
                icon=ft.icons.DOOR_FRONT_DOOR_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.DOOR_FRONT_DOOR_ROUNDED),
                label_content=ft.Text("Salir"),
            ),
        ],
        on_change=lambda e: print("Selected destination:", e.control.selected_index),
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Column([ ft.Text("Body!")], alignment=ft.MainAxisAlignment.START, expand=True),
            ],
            expand=True,
        )
    )

ft.app(target=main)