from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.footer_component import FooterComponent
from utils.helpers import parse_price


class ProductDetailsPage(BasePage):
    """Page Object for individual Product Details view."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.footer = FooterComponent(page)

        self.back_button: Locator = page.locator("[data-test='back-to-products']")
        self.item_name: Locator = page.locator(".inventory_details_name")
        self.item_description: Locator = page.locator(".inventory_details_desc")
        self.item_price: Locator = page.locator(".inventory_details_price")
        self.add_to_cart_button: Locator = page.locator(".inventory_details_container button:has-text('Add to cart')")
        self.remove_button: Locator = page.locator(".inventory_details_container button:has-text('Remove')")
        self.product_image: Locator = page.locator(".inventory_details_img")

    def is_loaded(self, timeout: int = 10000) -> bool:
        """Verifies product details page is loaded."""
        try:
            self.item_name.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_name(self) -> str:
        """Returns product name from details page."""
        self.item_name.wait_for(state="visible", timeout=5000)
        return self.item_name.inner_text().strip()

    def get_description(self) -> str:
        """Returns product description."""
        return self.item_description.inner_text().strip()

    def get_price(self) -> float:
        """Returns product price parsed as float."""
        return parse_price(self.item_price.inner_text().strip())

    def add_to_cart(self):
        """Clicks Add to Cart."""
        self.add_to_cart_button.click()

    def remove_from_cart(self):
        """Clicks Remove."""
        self.remove_button.click()

    def is_remove_displayed(self, timeout: int = 5000) -> bool:
        """Checks if Remove button is visible."""
        try:
            self.remove_button.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_add_to_cart_displayed(self, timeout: int = 5000) -> bool:
        """Checks if Add to cart button is visible."""
        try:
            self.add_to_cart_button.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def back_to_products(self):
        """Navigates back to inventory page."""
        self.back_button.click()
        self.page.wait_for_url("**/inventory.html", timeout=10000)
