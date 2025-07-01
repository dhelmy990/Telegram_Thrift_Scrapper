from .Auction import Post
import flet as ft

def subcard(post : Post):
    image_widget = ft.Image(
                src_base64 = post.flet_image(),
                width=200,
                height=200,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
                border_radius=ft.border_radius.all(10),
            )
    sub_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                image_widget,
                ft.Text(post.get_text()),
                ft.Text(f"Starting bid: {post.get_original_price()}", size=12),
                ft.Text(f"Current bid: {post.offer}", size=12),
            ], spacing=5),
            padding=10,
            border_radius=8,
        ),
        elevation=1,
    )

    return sub_card

def card(subcards, ready = False, username = None):
    if ready:
        color = ft.Colors.GREEN
        text = f"@{username}"
    else:
        color = ft.Colors.RED
        text = "Still bidding"
        subcards = [subcards]
    


    card_content = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(text, color=color, weight=ft.FontWeight.BOLD),
                            padding=ft.padding.only(right=10),
                        )
                    ]),
                    ft.ListView(subcards, height=200, auto_scroll = False),
                ], spacing=10),
                padding=10,
                bgcolor=ft.Colors.SURFACE,
                border_radius=8,
            ),
            elevation=2,
        )
    return card_content


