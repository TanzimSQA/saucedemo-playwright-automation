from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.footer_component import FooterComponent


class CheckoutStepOnePage(BasePage):
    """Page Object for Checkout Step One: Your Information."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.footer = FooterComponent(page)

        self.title_heading: Locator = page.locator("[data-test='title']")
        self.first_name_input: Locator = page.locator("[data-test='firstName']")
        self.last_name_input: Locator = page.locator("[data-test='lastName']")
        self.postal_code_input: Locator = page.locator("[data-test='postalCode']")
        self.continue_button: Locator = page.locator("[data-test='continue']")
        self.cancel_button: Locator = page.locator("[data-test='cancel']")
        self.error_message: Locator = page.locator("[data-test='error']")
        self.error_close_button: Locator = page.locator(".error-button")

    def is_loaded(self, timeout: int = 10000) -> bool:
        """Verifies checkout step one is displayed."""
        try:
            self.page.locator("[data-test='title']:has-text('Checkout: Your Information')").wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def fill_customer_info(self, first_name: str = "", last_name: str = "", postal_code: str = ""):
        """Fills checkout customer information fields."""
        if first_name:
            self.first_name_input.fill(first_name)
        else:
            self.first_name_input.clear()

        if last_name:
            self.last_name_input.fill(last_name)
        else:
            self.last_name_input.clear()

        if postal_code:
            self.postal_code_input.fill(postal_code)
        else:
            self.postal_code_input.clear()

    def click_continue(self):
        """Clicks Continue button."""
        self.continue_button.click()

    def click_cancel(self):
        """Clicks Cancel button."""
        self.cancel_button.click()

    def get_error_message(self) -> str:
        """Returns displayed validation error message."""
        return self.error_message.inner_text().strip()

    def is_error_displayed(self, timeout: int = 5000) -> bool:
        """Returns True if error container is visible."""
        try:
            self.error_message.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def dismiss_error(self):
        """Dismisses the error banner."""
        self.error_close_button.click()
        self.error_message.wait_for(state="hidden", timeout=3000)
