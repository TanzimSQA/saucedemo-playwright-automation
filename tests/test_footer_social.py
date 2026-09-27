import pytest
from pages.inventory_page import InventoryPage
from data.test_data import TestData


@pytest.mark.regression
class TestFooterSocial:
    """Test suite covering footer links, social networks, and copyright notice."""

    def test_twitter_social_link(self, authenticated_page: InventoryPage):
        """Verify Twitter link target and href."""
        link = authenticated_page.footer.twitter_link
        assert link.is_visible()
        assert link.get_attribute("target") == "_blank"
        assert TestData.SOCIAL_LINKS["twitter"] in authenticated_page.footer.get_twitter_href()

    def test_facebook_social_link(self, authenticated_page: InventoryPage):
        """Verify Facebook link target and href."""
        link = authenticated_page.footer.facebook_link
        assert link.is_visible()
        assert link.get_attribute("target") == "_blank"
        assert TestData.SOCIAL_LINKS["facebook"] in authenticated_page.footer.get_facebook_href()

    def test_linkedin_social_link(self, authenticated_page: InventoryPage):
        """Verify LinkedIn link target and href."""
        link = authenticated_page.footer.linkedin_link
        assert link.is_visible()
        assert link.get_attribute("target") == "_blank"
        assert TestData.SOCIAL_LINKS["linkedin"] in authenticated_page.footer.get_linkedin_href()

    def test_footer_copyright_notice(self, authenticated_page: InventoryPage):
        """Verify copyright statement is displayed in footer."""
        copyright_text = authenticated_page.footer.get_copyright_text()
        assert "Sauce Labs. All Rights Reserved." in copyright_text
        assert "Terms of Service" in copyright_text
