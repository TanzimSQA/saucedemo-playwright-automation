from typing import List
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.footer_component import FooterComponent
from utils.helpers import parse_price


class CheckoutStepTwoPage(BasePage):
    """Page Object for Checkout Step Two: Overview."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.footer = FooterComponent(page)

        self.title_heading: Locator = page.locator("[data-test='title']")
        self.cart_items: Locator = page.locator(".cart_item")
        self.item_names: Locator = page.locator(".inventory_item_name")
        self.item_prices: Locator = page.locator(".inventory_item_price")
        self.payment_info_label: Locator = page.locator("[data-test='payment-info-value']")
        self.shipping_info_label: Locator = page.locator("[data-test='shipping-info-value']")
        self.subtotal_label: Locator = page.locator(".summary_subtotal_label")
        self.tax_label: Locator = page.locator(".summary_tax_label")
        self.total_label: Locator = page.locator(".summary_total_label")
        self.finish_button: Locator = page.locator("[data-test='finish']")
        self.cancel_button: Locator = page.locator("[data-test='cancel']")

    def is_loaded(self, timeout: int = 10000) -> bool:
        """Verifies checkout overview page is displayed."""
        try:
            self.title_heading.wait_for(state="visible", timeout=timeout)
            return self.title_heading.inner_text().strip() == "Checkout: Overview"
        except Exception:
            return False

    def get_item_names(self) -> List[str]:
        """Returns names of products displayed on overview."""
        return [self.item_names.nth(i).inner_text().strip() for i in range(self.item_names.count())]

    def get_item_prices(self) -> List[float]:
        """Returns prices of products displayed on overview."""
        return [parse_price(self.item_prices.nth(i).inner_text().strip()) for i in range(self.item_prices.count())]

    def get_subtotal(self) -> float:
        """Returns parsed subtotal amount."""
        return parse_price(self.subtotal_label.inner_text())

    def get_tax(self) -> float:
        """Returns parsed tax amount."""
        return parse_price(self.tax_label.inner_text())

    def get_total(self) -> float:
        """Returns parsed grand total amount."""
        return parse_price(self.total_label.inner_text())

    def get_payment_info(self) -> str:
        """Returns payment info text."""
        return self.payment_info_label.inner_text().strip()

    def get_shipping_info(self) -> str:
        """Returns shipping info text."""
        return self.shipping_info_label.inner_text().strip()

    def click_finish(self):
        """Clicks Finish button."""
        self.finish_button.click()

    def click_cancel(self):
        """Clicks Cancel button."""
        self.cancel_button.click()
