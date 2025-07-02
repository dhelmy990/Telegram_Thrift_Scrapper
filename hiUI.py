import flet as ft


async def main(page: ft.Page):
    with open('icons.txt', 'w') as f:
        f.write(str(dir(ft.Icons)))
    
    

ft.app(target=main) 