import flet as ft
from config.secrets import channel_unofficial_name
import col


def main(page: ft.Page):
    
    page.title = channel_unofficial_name
    page.bgcolor = ft.Colors.with_opacity(1.0, col.buff)
    page.padding = page.width * 0.1
    page.update()

ft.app(target=main)