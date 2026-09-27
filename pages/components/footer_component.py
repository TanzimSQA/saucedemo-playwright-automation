from playwright.sync_api import Page, Locator


class FooterComponent:
    """Footer component present on authenticated pages."""

    def __init__(self, page: Page):
        self.page = page
        self.twitter_link: Locator = page.locator("a[data-test='social-x'], a[data-test='social-twitter']")
        self.facebook_link: Locator = page.locator("a[data-test='social-facebook']")
        self.linkedin_link: Locator = page.locator("a[data-test='social-linkedin']")
        self.footer_copy: Locator = page.locator(".footer_copy, [data-test='footer-copy']")

    def get_twitter_href(self) -> str:
        return self.twitter_link.get_attribute("href") or ""

    def get_facebook_href(self) -> str:
        return self.facebook_link.get_attribute("href") or ""

    def get_linkedin_href(self) -> str:
        return self.linkedin_link.get_attribute("href") or ""

    def get_copyright_text(self) -> str:
        return self.footer_copy.inner_text().strip()
