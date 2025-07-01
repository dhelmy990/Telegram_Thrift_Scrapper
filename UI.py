import flet as ft
from utils.Auction import *
import bill
import asyncio
from collections import defaultdict
from client import client, get_username

ORDER_STAGES = [
    "Active Bids",
    "Pending Payment",
    "To Pack",
    "Order Completed",
]

# State: places the orders in each stage
class OrderState:
    def __init__(self):
        self.orders = defaultdict(list)
        
    async def load(self):
        claimed_dict, unclaimed_list = await bill.active_posts()
        self.orders[ORDER_STAGES[0]] = claimed_dict

    def move_order(self, order_id, from_stage, to_stage):
        for order in self.orders[from_stage]:
            if order["id"] == order_id:
                self.orders[from_stage].remove(order)
                self.orders[to_stage].append(order)
                return order
        return None
     
class PostDraggableFactory():
    @staticmethod
    def create(post_items):
        if isinstance(post_items, dict):
            return [BiddedDraggable(post_item) for post_item in post_items.items()]
        else:
            return
            print(type(post_items))
            print(post_items)
            raise SyntaxError()
        
        
class PostDraggableAborter():
    pass


class UnbiddedDraggable(ft.Draggable):
    pass

class BiddedDraggable(ft.Draggable):
    def __init__(self, id_to_post: tuple, on_drag_start=None, **kwargs):
        self.buyer_username = id_to_post[1][0].best_buyer_name
        self.posts = id_to_post[1]

        # Subcards for each post
        subcards = []
        for post in self.posts:
            image_widget = ft.Image(
                src_base64 = post.flet_image(),
                width=200,
                height=200,
                fit=ft.ImageFit.COVER,
                repeat=ft.ImageRepeat.NO_REPEAT,
                border_radius=ft.border_radius.all(10),
            )
            subcard = ft.Card(
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
            subcards.append(subcard)

        card_content = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"@{self.buyer_username}", color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD),
                            padding=ft.padding.only(right=10),
                        ),
                        ft.Text("Bids", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.ListView(subcards, height=200),
                ], spacing=10),
                padding=10,
                bgcolor=ft.Colors.SURFACE,
                border_radius=8,
            ),
            elevation=2,
        )

        super().__init__(
            group="orders",
            data={"id": self.buyer_username, "from_stage": "Active Bids"},
            content=card_content,
            on_drag_start=on_drag_start,
            **kwargs
        )
    
    def refresh_display(self):
        # Update UI when post data changes
        pass



def create_column(stage, orders, on_accept, on_update=None):
    # Column header
    header = ft.Text(stage, size=18, weight=ft.FontWeight.BOLD)
    # Order cards
    order_cards = PostDraggableFactory.create(orders)
    #TODO check for unbought later
    
    # Drag target for dropping cards
    drag_target = ft.DragTarget(
        group="orders",
        content=ft.Column(order_cards, spacing=10),
        on_accept=on_accept,
        on_will_accept=lambda e: True,
        on_leave=lambda e: None,
        on_move=lambda e: None
    )
    # Add Update button for Active Bids
    children = [header, drag_target]
    if on_update and stage == "Active Bids":
        children.append(
            ft.ElevatedButton("Update!", on_click=on_update, bgcolor=ft.Colors.PRIMARY)
        )
    return ft.Container(
        content=ft.Column(children, spacing=15),
        border=ft.border.all(2, ft.Colors.OUTLINE),
        border_radius=10,
        padding=15,
        expand=True,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        margin=5,
    )

async def main(page: ft.Page):
    await client.start()
    page.title = "Order Tracker Workstation"
    page.bgcolor = ft.Colors.SURFACE
    page.scroll = ft.ScrollMode.AUTO
    state = OrderState()
    await state.load()

    def refresh():
        # Rebuild the UI with the current state
        page.controls.clear()
        page.controls.append(
            ft.Container(
                content=ft.Text(
                    "Order Tracker Workstation",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=ft.padding.only(top=20, bottom=20),
            )
        )
        # Row of columns
        def make_on_accept(stage):
            def on_accept(e):
                """
                """
                print('on accept')
                data = e.data
                if isinstance(data, str):
                    import json
                    data = json.loads(data.replace("'", '"'))
                order_id = data["id"]
                from_stage = data["from_stage"]
                if from_stage != stage:
                    state.move_order(order_id, from_stage, stage)
                    refresh()
            return on_accept

        def on_update(e):
            page.snack_bar = ft.SnackBar(ft.Text("Update clicked!"))
            page.snack_bar.open = True
            page.update()

        row = ft.Row(
            [
                create_column(
                    stage,
                    state.orders[stage],
                    on_accept=make_on_accept(stage),
                    on_update=on_update if stage == "Active Bids" else None,
                )
                for stage in ORDER_STAGES
            ],
            expand=True,
            spacing=10,
        )
        page.controls.append(row)
        page.update()

    refresh()

ft.app(target=main) 