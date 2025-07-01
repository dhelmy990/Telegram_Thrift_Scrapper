import flet as ft
from utils.Auction import *
from utils.UIutils import subcard, card
import bill
import asyncio
from collections import defaultdict
from client import client, get_username
import json

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


    def change_stage(self, order, fro, to):
        #change stage
        self.orders[fro].remove(order)
        self.orders[to].append(order)

        #change data
        
    async def load(self):
        new_posts = await bill.active_posts()
        for new in new_posts:
            self.orders[ORDER_STAGES[0]].append(new)

    def move_order(self, order_id, from_stage, to_stage):
        #TODO what did they give you fucking hashmaps for. This is O(n). You deserve your unemployment.
        print(self.orders[from_stage])
        for order in self.orders[from_stage]:
            #this line identifies it based on the two cases: the id is a username, or the id is the root of that single post. 
            #I promise, I will truly, never, ever engineer software in python again
            #I was wrong. Java and JavaScript are actually pretty good languages.
            #No one should ever have to write anything meant for a UI in this cursed fucking langauge where i can set what was formerly a dictionary to my custom class
            print(order, from_stage)
            if order[0] is None:
                if order_id == order[1].get_root():
                    self.change_stage(order, from_stage, to_stage)
                    return order
            else:
                if order_id == order[1][0].load_best_buyer(): 
                    self.change_stage(order, from_stage, to_stage)
                    return order
        return None
     
class PostDraggableFactory():
    @staticmethod
    def create(post_items, stage):
        if not isinstance(post_items, tuple):
            raise Exception("Post items is not a tuple")
        
        if post_items[0] is None:
            return UnbiddedDraggable(post_items[1])
        else:
            return BiddedDraggable(post_items, stage) 
        
        
        
class PostDraggableAborter():
    pass

def UnbiddedDraggable(post: Post, on_drag_start=None, **kwargs):
    # Use the same card layout as before, but with a header-only draggable overlay
    card_width = 270
    header_height = 50
    # Build the card (not ready, no username)
    card_content = card(subcard(post), ready=False, username=None)

    overlay_draggable = ft.Draggable(
        group="orders",
        data={"id": post.get_root(), "from_stage": "Active Bids"},
        content=ft.Container(
            width=card_width,
            height=header_height,
            bgcolor=ft.Colors.with_opacity(0.01, ft.Colors.BLUE),
        ),
        content_feedback=ft.Container(
            width=card_width,
            height=header_height,
            bgcolor=ft.Colors.BLUE,
            content=ft.Text("Still bidding", color=ft.Colors.WHITE, size=16),
            border_radius=8,
            alignment=ft.alignment.center,
        ),
        on_drag_start=on_drag_start,
        **kwargs
    )

    return ft.Stack([
        card_content,
        overlay_draggable,
    ], width=card_width)

def BiddedDraggable(id_to_post, stage, on_drag_start=None, **kwargs):
    buyer_username = id_to_post[1][0].best_buyer_name
    posts = id_to_post[1]
    subcards = [subcard(post) for post in posts]
    card_content = card(subcards, True, buyer_username)

    header_height = 50
    card_width = 270

    # Draggable overlay only on header
    overlay_draggable = ft.Draggable(
        group="orders",
        data = {"id": buyer_username, "from_stage": stage},
        content=ft.Container(
            width=card_width,
            height=header_height,
            bgcolor=ft.Colors.with_opacity(0.01, ft.Colors.BLUE),
        ),
        content_feedback=ft.Container(
            width=card_width,
            height=header_height,
            bgcolor=ft.Colors.BLUE,
            content=ft.Text(f"@{buyer_username}", color=ft.Colors.WHITE, size=16),
            border_radius=8,
            alignment=ft.alignment.center,
        ),
        on_drag_start=on_drag_start,
        **kwargs
    )

    return ft.Stack(
        [
            card_content,
            overlay_draggable,  # This will be at the top of the stack, aligned with the header
        ],
        width=card_width,
        # No height constraint!
    )

def create_column(stage, orders : list[tuple], on_accept, on_update=None):
    # Column header
    header = ft.Text(stage, size=18, weight=ft.FontWeight.BOLD)
    # Order cards
    order_cards = []
    for order in orders:
        order_cards.append(PostDraggableFactory.create(order, stage))
        #TODO check for unbought later
    

    # Drag target for dropping cards
    # If no cards present, content will be set to a plus sign
    if len(order_cards) == 0:
        content = ft.Container(
            content=ft.Icon(ft.Icons.ADD, size=80, color=ft.Colors.GREY_600),
            alignment=ft.alignment.center,
            padding=20,
            border=ft.border.all(2, ft.Colors.GREY_400),
            border_radius=10,
        )
    else:
        content = ft.Column(order_cards, spacing=10)

    drag_target = ft.DragTarget(
        group="orders",
        content=content,
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
                e = page.get_control(e.src_id)
                data = e.data
                order_id = data["id"]
                from_stage = data["from_stage"]
                print(e.data)
                
                if from_stage != stage:
                    change = state.move_order(order_id, from_stage, stage)
                    e.data["from_stage"] = stage
                    
                    if change is not None: 
                        print(str(e.data) + "again")     
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