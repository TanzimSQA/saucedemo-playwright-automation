from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the SauceDemo Login Page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input: Locator = page.locator("[data-test='username']")
        self.password_input: Locator = page.locator("[data-test='password']")
        self.login_button: Locator = page.locator("[data-test='login-button']")
        self.error_message: Locator = page.locator("[data-test='error']")
        self.error_close_button: Locator = page.locator(".error-button")
        self.login_credentials_container: Locator = page.locator("#login_credentials")
        self.login_password_container: Locator = page.locator(".login_password")

    def load(self, base_url: str = "https://www.saucedemo.com"):
        """Navigates to the SauceDemo home/login page."""
        self.navigate(base_url)

    def login(self, username: str, password: str):
        """Fills credentials and clicks the login button."""
        if username:
            self.username_input.fill(username)
        else:
            self.username_input.clear()

        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        self.login_button.click()

    def get_error_message_text(self) -> str:
        """Returns visible error text."""
        return self.error_message.inner_text().strip()

    def is_error_displayed(self, timeout: int = 5000) -> bool:
        """Checks if the error container is currently visible."""
        try:
            self.error_message.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def dismiss_error(self):
        """Dismisses the error banner using the 'X' button."""
        self.error_close_button.click()
        self.error_message.wait_for(state="hidden", timeout=3000)

    def is_login_button_visible(self, timeout: int = 5000) -> bool:
        """Checks if the login button is visible."""
        try:
            self.login_button.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False
