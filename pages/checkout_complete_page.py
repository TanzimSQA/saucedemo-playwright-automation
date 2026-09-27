from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.footer_component import FooterComponent


class CheckoutCompletePage(BasePage):
    """Page Object for Checkout: Complete!"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.footer = FooterComponent(page)

        self.title_heading: Locator = page.locator("[data-test='title']")
        self.complete_header: Locator = page.locator("[data-test='complete-header']")
        self.complete_text: Locator = page.locator("[data-test='complete-text']")
        self.pony_express_img: Locator = page.locator("img[data-test='pony-express']")
        self.back_home_btn: Locator = page.locator("[data-test='back-to-products']")
        self.generate_pdf_btn: Locator = page.locator("[data-test='generate-pdf-order']")

    def is_loaded(self, timeout: int = 10000) -> bool:
        """Verifies checkout complete page is displayed."""
        try:
            self.page.locator("[data-test='title']:has-text('Checkout: Complete!')").wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_order_complete_header(self) -> str:
        """Returns the primary thank you text."""
        return self.complete_header.inner_text().strip()

    def get_order_complete_text(self) -> str:
        """Returns the dispatch notification text."""
        return self.complete_text.inner_text().strip()

    def is_pony_express_image_visible(self, timeout: int = 5000) -> bool:
        """Checks if pony express image is displayed."""
        try:
            self.pony_express_img.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def click_back_home(self):
        """Clicks Back Home button."""
        self.back_home_btn.click()
