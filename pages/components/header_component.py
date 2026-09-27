from playwright.sync_api import Page, Locator


class HeaderComponent:
    """Header component present across authenticated pages."""

    def __init__(self, page: Page):
        self.page = page
        self.burger_menu_button: Locator = page.locator("#react-burger-menu-btn")
        self.app_logo: Locator = page.locator(".app_logo")
        self.shopping_cart_link: Locator = page.locator(".shopping_cart_link")
        self.shopping_cart_badge: Locator = page.locator(".shopping_cart_badge")

    def open_sidebar_menu(self):
        """Clicks the hamburger menu button."""
        self.burger_menu_button.click()
        self.page.wait_for_selector(".bm-menu-wrap", state="visible")

    def click_shopping_cart(self):
        """Clicks the shopping cart icon."""
        self.shopping_cart_link.click()

    def get_cart_badge_count(self) -> int:
        """Returns the number shown on the shopping cart badge or 0 if absent."""
        if self.shopping_cart_badge.is_visible():
            return int(self.shopping_cart_badge.inner_text().strip())
        return 0

    def is_cart_badge_visible(self) -> bool:
        """Checks if the cart badge is currently visible."""
        return self.shopping_cart_badge.is_visible()
