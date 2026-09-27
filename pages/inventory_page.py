from typing import List
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.sidebar_component import SidebarComponent
from pages.components.footer_component import FooterComponent
from utils.helpers import parse_price


class InventoryPage(BasePage):
    """Page Object for the SauceDemo Inventory (Products) Page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.sidebar = SidebarComponent(page)
        self.footer = FooterComponent(page)

        self.title_heading: Locator = page.locator("[data-test='title']")
        self.sort_select: Locator = page.locator("[data-test='product-sort-container']")
        self.inventory_items: Locator = page.locator(".inventory_item")
        self.item_names: Locator = page.locator(".inventory_item_name")
        self.item_prices: Locator = page.locator(".inventory_item_price")
        self.item_descriptions: Locator = page.locator(".inventory_item_desc")

    def is_loaded(self, timeout: int = 10000) -> bool:
        """Verifies inventory page title heading is visible."""
        try:
            self.title_heading.wait_for(state="visible", timeout=timeout)
            return self.title_heading.inner_text().strip() == "Products"
        except Exception:
            return False

    def get_product_names(self) -> List[str]:
        """Returns all product titles on page."""
        return [self.item_names.nth(i).inner_text().strip() for i in range(self.item_names.count())]

    def get_product_prices(self) -> List[float]:
        """Returns all product prices as float list."""
        return [parse_price(self.item_prices.nth(i).inner_text().strip()) for i in range(self.item_prices.count())]

    def select_sort_option(self, option_value: str):
        """Selects sorting option from dropdown ('az', 'za', 'lohi', 'hilo')."""
        self.sort_select.select_option(option_value)

    def get_product_card(self, product_name: str) -> Locator:
        """Locates specific inventory item card containing product name."""
        return self.inventory_items.filter(has_text=product_name).first

    def add_product_to_cart(self, product_name: str):
        """Clicks Add to cart on product card matching name."""
        card = self.get_product_card(product_name)
        card.locator("button:has-text('Add to cart')").click()

    def remove_product_from_cart(self, product_name: str):
        """Clicks Remove button on product card matching name."""
        card = self.get_product_card(product_name)
        card.locator("button:has-text('Remove')").click()

    def is_remove_button_displayed(self, product_name: str, timeout: int = 5000) -> bool:
        """Checks if the Remove button is shown for specified item."""
        try:
            card = self.get_product_card(product_name)
            card.locator("button:has-text('Remove')").wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_add_to_cart_button_displayed(self, product_name: str, timeout: int = 5000) -> bool:
        """Checks if the Add to cart button is shown for specified item."""
        try:
            card = self.get_product_card(product_name)
            card.locator("button:has-text('Add to cart')").wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def open_product_details_by_name(self, product_name: str):
        """Clicks product name link to open product details."""
        card = self.get_product_card(product_name)
        card.locator(".inventory_item_name").click()
        self.page.wait_for_url("**/inventory-item.html*", timeout=10000)

    def open_product_details_by_image(self, product_name: str):
        """Clicks product image link to open product details."""
        card = self.get_product_card(product_name)
        card.locator(".inventory_item_img a").click()
        self.page.wait_for_url("**/inventory-item.html*", timeout=10000)
