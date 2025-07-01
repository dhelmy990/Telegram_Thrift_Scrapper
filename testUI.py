import flet as ft

def main(page: ft.Page):
    def on_accept(e):
        print("Dropped:", e.data)

    draggable = ft.Draggable(
        group="orders",
        content=ft.Container(
            content=ft.Text("Drag me!"),
            width=100,
            height=50,
            bgcolor=ft.Colors.BLUE,
        ),
        data="my_draggable"
    )

    drag_target = ft.DragTarget(
        group="orders",
        content=ft.Container(
            content=ft.Text("Drop here!"),
            width=200,
            height=100,
            bgcolor=ft.Colors.YELLOW,
        ),
        on_accept=on_accept
    )

    page.add(draggable, drag_target)

ft.app(target=main)