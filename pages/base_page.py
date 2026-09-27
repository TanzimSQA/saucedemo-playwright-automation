from playwright.sync_api import Page, Locator, expect


class BasePage:
    """Base class for all Page Objects providing common browser interactions."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        """Navigate to specified URL and wait for DOM content loaded."""
        self.page.goto(url, wait_until="domcontentloaded")

    @property
    def current_url(self) -> str:
        """Returns the current URL."""
        return self.page.url

    @property
    def page_title(self) -> str:
        """Returns the page title."""
        return self.page.title()

    def wait_for_url_contains(self, partial_url: str, timeout: int = 10000):
        """Wait until current URL contains expected text."""
        self.page.wait_for_url(f"**/*{partial_url}*", timeout=timeout)

    def take_screenshot(self, filepath: str):
        """Takes a full page screenshot saved to filepath."""
        self.page.screenshot(path=filepath, full_page=True)

    def reload(self):
        """Reloads current page."""
        self.page.reload(wait_until="domcontentloaded")
