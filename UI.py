import flet as ft
from utils.Auction import *
from utils.UIutils import subcard, card
import bill
from time import sleep
from bill import send_order
from collections import defaultdict 
from utils.collect_utils import load_pickles
import json
import subprocess
import asyncio

ORDER_STAGES = [
    "Active Bids",
    "Pending Payment",
    "To Pack",
    "Order Completed"
]
    

def clientise(order, stage):
    if stage == 1:
        print('attempt')
        subprocess.run(["python3", "bill.py", 'bill_customer', '--user_id', str(order[0])])
    
        


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
        #new_posts = await bill.active_posts()
        new_posts = load_pickles()
        for new in new_posts:
            self.orders[ORDER_STAGES[0]].append(new)
    
    @staticmethod
    def valid_move(order_id, from_stage, to_stage):
        fro = ORDER_STAGES.index(from_stage)
        to = ORDER_STAGES.index(to_stage)

        if to - fro != 1:
            return False
        return not isinstance(order_id, int)
        
        
    


    def check_swap(self, order_id, from_stage, to_stage):
        #TODO what did they give you fucking hashmaps for. This is O(n). You deserve your unemployment.
        #print(self.orders[from_stage])
        if not OrderState.valid_move(order_id, from_stage, to_stage):
            return None

        for order in self.orders[from_stage]:
            #this line identifies it based on the two cases: the id is a username, or the id is the root of that single post. 
            #I promise, I will truly, never, ever engineer software in python again
            #I was wrong. Java and JavaScript are actually pretty good languages.
            #No one should ever have to write anything meant for a UI in this cursed fucking langauge where i can set what was formerly a dictionary to my custom class
            print(order, from_stage)
            if order[0] is not None: #this is now redundant
                if order_id == order[1][0].load_best_buyer():
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
    if stage == "Order Completed":
        content = ft.Container(
            content=ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=80, color=ft.Colors.GREY_600),
            alignment=ft.alignment.center,
            padding=20,
            border=ft.border.all(2, ft.Colors.GREY_400),
            border_radius=10,
        )
    elif len(order_cards) == 0:
        content = ft.Container(
            content=ft.Icon(ft.Icons.ADD, size=80, color=ft.Colors.GREY_600),
            alignment=ft.alignment.center,
            padding=20,
            border=ft.border.all(2, ft.Colors.GREY_400),
            border_radius=10,
        )
    else:
        # Create a container with the cards and a drop zone indicator
        content = ft.Container(
            content=ft.Column([
                ft.Column(order_cards, spacing=10),
                # Add a visible drop zone at the bottom
                ft.Container(
                    content=ft.Text("Drop here", size=14, color=ft.Colors.GREY_600),
                    alignment=ft.alignment.center,
                    padding=10,
                    border=ft.border.all(2, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                    margin=ft.margin.only(top=10),
                )
            ], spacing=5),
            padding=10,
        )

    drag_target = ft.DragTarget(
        group="orders",
        content=content,
        on_accept=on_accept,
        on_will_accept=lambda e: True,
        on_leave=lambda e: None,
        on_move=lambda e: None,
    )
    
    # Create a container for the drag target with visual feedback
    drag_target_container = ft.Container(
        content=drag_target,
        border=ft.border.all(2, ft.Colors.BLUE_200),
        border_radius=8,
        padding=5,
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.BLUE),
    )
    # Add Update button for Active Bids
    children = [header, drag_target_container]
    if on_update and stage == ORDER_STAGES[0]:
        children.append(
            ft.ElevatedButton("Update!", on_click=on_update, bgcolor=ft.Colors.PRIMARY)
        )
    return ft.Container(
        content=ft.Column(children, spacing=15),
        border=ft.border.all(2, ft.Colors.OUTLINE),
        border_radius=10,
        padding=15,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
        margin=5
    )

def get_address_event(order, page, result, lookback = 10):
    # Create the image widget
    customers_nums = subprocess.Popen(['python3', 'bill.py', 'scrape_chat', 
                                       '--user_id', str(order[0]), 
                                       '--lookback', str(lookback)], 
                                      stdout = subprocess.PIPE, text = True)
    name_f, phone_f, address_f = ft.TextField(label="Name", value = order[1][0].best_buyer_name), ft.TextField(label="Phone number"), ft.TextField(label="Address", multiline=True, min_lines=2, max_lines=3)
    fattybox = ft.Checkbox(label="Bulky item", value=False)
    def submit_address(e):
        if not (name_f.value is None or not phone_f.value.isdigit() or len(phone_f.value) != 8 or address_f.value is None):
            result["name"] = name_f.value
            result["phone"] = phone_f.value
            result["address"] = address_f.value
            result["ninjaVan"] = fattybox.value
            result["completed"] = True
    def handle_dismiss(e):
        print("LET ME GO")
        result["completed"] = True


    image_widget = ft.Image(
        src_base64=order[1][0].flet_image(),
        width=200,
        height=200,
        fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.all(10),
    )
        
    # Create the dialog
    
       

    dialog = ft.AlertDialog(
        modal=False,
        content=ft.Container(
            width=350,
            padding=20,
            content=ft.Column(
                [
                    ft.Row([image_widget], alignment = ft.MainAxisAlignment.CENTER)
                    ,
                    name_f,
                    phone_f,
                    address_f,
                    ft.Row(
                        [
                            ft.OutlinedButton(text = "Ok!", on_click = submit_address),
                            fattybox,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
                spacing=10,
            ),
        ),
        on_dismiss=handle_dismiss,
    )


    info, error = customers_nums.communicate()
    if error is None:
        print('free!')
        info = info.split('\n')
        phone_f.value = info[0]
        address_f.value  = info[1]

    # Show the dialog
    if page:
        page.open(dialog)

    while not result["completed"]:
        sleep(0.1)  # Check every 100ms
        page.update()

    page.close(dialog)
    # If you don't have access to page here, you may need to pass it in as an argument.

async def main(page: ft.Page):
    
    page.title = "Order Tracker Workstation"
    page.bgcolor = ft.Colors.SURFACE
    page.scroll = ft.ScrollMode.AUTO
    state = OrderState()
    page.window.full_screen = True
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
        def make_on_accept(to_stage):
            def on_accept(e):
                e = page.get_control(e.src_id)
                data = e.data
                order_id = data["id"]
                from_stage = data["from_stage"]
                print(e.data)

                order = state.check_swap(order_id, from_stage, to_stage)
                #one last check, for the stage
                if to_stage == ORDER_STAGES[2]:
                    result = {"completed": False}
                    get_address_event(order, e.page, result)
                    if result.get("address") is None: order = None


                if order is None:
                    return #for whatever reason, change nothing
                
                state.change_stage(order, from_stage, to_stage)
                clientise(order, ORDER_STAGES.index(to_stage))
                e.data["from_stage"] = to_stage 
                print(str(e.data) + "Moved")     
                if to_stage == ORDER_STAGES[3]:
                    print("Order Completed!")
                    #print(state.orders[ORDER_STAGES[3]])
                    page.open(ft.SnackBar(ft.Text("Order Completed!")))
                    page.update()
                refresh()

            return on_accept
        
        

        def get_orders(e):
            # Find the Stack parent (the column's direct parent)
            stack = e.control
            while stack and not isinstance(stack, ft.Stack):
                stack = stack.parent
            if not stack:
                print("Could not find stack parent!")
                return
            # Add overlay and progress ring
            overlay = ft.Container(bgcolor=ft.Colors.BLACK, opacity=0.7, expand=True)
            ring = ft.ProgressRing(width=60, height=60, color=ft.Colors.WHITE)
            overlay_container = ft.Container(content=ring, alignment=ft.alignment.center, expand=True)
            stack.controls.append(overlay)
            stack.controls.append(overlay_container)
            stack.update()
            from threading import Timer

            def remove_overlay():
                # Remove the last two controls (overlay and ring)
                if overlay in stack.controls:
                    stack.controls.remove(overlay)
                if overlay_container in stack.controls:
                    stack.controls.remove(overlay_container)
                stack.update()
            
            timer = Timer(3.0, remove_overlay)
            timer.start()

        row = ft.Row(
            [
                ft.Stack(
                    [
                    create_column(
                            stage,
                            state.orders[stage],
                            on_accept=make_on_accept(stage),
                            on_update=get_orders if stage == ORDER_STAGES[0] else None,
                        )
                    ],
                    expand = True
                )
                
                for stage in ORDER_STAGES
            ],
            expand=True,
            spacing=10,
        )

        row_container = ft.Container(
            height = page.height - 200,
            content = row,
            expand=True,
        )
        page.controls.append(row_container)
        page.update()

    refresh()

ft.app(target=main) 