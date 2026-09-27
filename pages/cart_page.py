from typing import List, Dict
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.sidebar_component import SidebarComponent
from pages.components.footer_component import FooterComponent
from utils.helpers import parse_price


class CartPage(BasePage):
    """Page Object for the Shopping Cart Page (/cart.html)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.sidebar = SidebarComponent(page)
        self.footer = FooterComponent(page)

        self.title_heading: Locator = page.locator("[data-test='title']")
        self.cart_items: Locator = page.locator(".cart_item")
        self.continue_shopping_btn: Locator = page.locator("[data-test='continue-shopping']")
        self.checkout_btn: Locator = page.locator("[data-test='checkout']")

    def is_loaded(self, timeout: int = 10000) -> bool:
        """Verifies cart page is displayed."""
        try:
            self.title_heading.wait_for(state="visible", timeout=timeout)
            return self.title_heading.inner_text().strip() == "Your Cart"
        except Exception:
            return False

    def get_cart_item_count(self) -> int:
        """Returns the number of item cards displayed in the cart."""
        self.is_loaded()
        return self.cart_items.count()

    def get_cart_items_info(self) -> List[Dict[str, any]]:
        """Returns a list of dicts with name, price, quantity for each cart item."""
        items = []
        count = self.cart_items.count()
        for i in range(count):
            item = self.cart_items.nth(i)
            name = item.locator(".inventory_item_name").inner_text().strip()
            price = parse_price(item.locator(".inventory_item_price").inner_text().strip())
            qty = int(item.locator(".cart_quantity").inner_text().strip())
            items.append({"name": name, "price": price, "quantity": qty})
        return items

    def get_item_card_by_name(self, product_name: str) -> Locator:
        """Locates specific cart item card matching product name."""
        return self.cart_items.filter(has_text=product_name).first

    def remove_item(self, product_name: str):
        """Clicks Remove button for specific product in cart."""
        card = self.get_item_card_by_name(product_name)
        card.locator("button:has-text('Remove')").click()

    def click_continue_shopping(self):
        """Clicks the 'Continue Shopping' button."""
        self.continue_shopping_btn.click()

    def click_checkout(self):
        """Clicks the 'Checkout' button."""
        self.checkout_btn.click()
