from playwright.sync_api import Page, Locator


class SidebarComponent:
    """Sidebar navigation menu component."""

    def __init__(self, page: Page):
        self.page = page
        self.menu_wrap: Locator = page.locator(".bm-menu-wrap")
        self.all_items_link: Locator = page.locator("#inventory_sidebar_link")
        self.about_link: Locator = page.locator("#about_sidebar_link")
        self.logout_link: Locator = page.locator("#logout_sidebar_link")
        self.reset_app_state_link: Locator = page.locator("#reset_sidebar_link")
        self.close_button: Locator = page.locator("#react-burger-cross-btn")

    def click_all_items(self):
        """Clicks the 'All Items' sidebar link."""
        self.all_items_link.click()

    def click_about(self):
        """Clicks the 'About' sidebar link."""
        self.about_link.click()

    def get_about_url(self) -> str:
        """Returns the href attribute of the About link."""
        return self.about_link.get_attribute("href") or ""

    def click_logout(self):
        """Clicks the 'Logout' sidebar link."""
        self.logout_link.click()

    def click_reset_app_state(self):
        """Clicks the 'Reset App State' sidebar link."""
        self.reset_app_state_link.click()

    def close_menu(self):
        """Closes the sidebar menu."""
        self.close_button.click()
        self.menu_wrap.wait_for(state="hidden", timeout=5000)

    def is_menu_visible(self, timeout: int = 4000) -> bool:
        """Returns whether the menu container is visible."""
        try:
            self.menu_wrap.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False
