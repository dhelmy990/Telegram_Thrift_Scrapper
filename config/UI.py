class BiddedDraggable(ft.Draggable):
    def __init__(self, buyer_username, posts, on_drag_start=None, **kwargs):
        self.buyer_username = buyer_username
        self.posts = posts

        # Subcards for each post
        subcards = []
        for i, post in enumerate(self.posts):
            images = post.get_all_images()
            if images and images[0]:
                # Use the actual image from the post
                image_widget = ft.Image(
                    src=images[0],
                    width=200,
                    height=200,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(10),
                )
            else:
                # Fallback to test image
                image_widget = ft.Image(
                    src=f"https://picsum.photos/200/200?{i}",
                    width=200,
                    height=200,
                    fit=ft.ImageFit.COVER,
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
                    ft.ListView(subcards, height=200, scroll="auto"),
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
    
    @classmethod
    async def create(cls, id_to_post: tuple, on_drag_start=None, **kwargs):
        """Factory method to create BiddedDraggable with async username fetching"""
        buyer_id, posts = id_to_post
        buyer_username = await get_username(buyer_id)
        return cls(buyer_username, posts, on_drag_start, **kwargs)
    
    def refresh_display(self):
        # Update UI when post data changes
        pass 

class PostDraggableFactory():
    @staticmethod
    async def create(post_items):
        if isinstance(post_items, dict):
            draggables = []
            for post_item in post_items.items():
                draggable = await BiddedDraggable.create(post_item)
                draggables.append(draggable)
            return draggables
        else:
            print(type(post_items))
            print(post_items)
            raise SyntaxError() 

async def create_column(stage, orders, on_accept, on_update=None):
    # Column header
    header = ft.Text(stage, size=18, weight=ft.FontWeight.BOLD)
    # Order cards
    order_cards = await PostDraggableFactory.create(orders)
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