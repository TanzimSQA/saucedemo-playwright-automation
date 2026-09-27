import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from data.test_data import TestData


@pytest.mark.sidebar
class TestSidebarNavigation:
    """Test suite covering sidebar/hamburger menu features and app state reset."""

    def test_open_and_close_sidebar_menu(self, authenticated_page: InventoryPage):
        """Verify opening and closing the hamburger menu."""
        authenticated_page.header.open_sidebar_menu()
        assert authenticated_page.sidebar.is_menu_visible()

        authenticated_page.sidebar.close_menu()
        # Menu should not be visible anymore
        assert not authenticated_page.sidebar.is_menu_visible()

    def test_about_link_points_to_saucelabs(self, authenticated_page: InventoryPage):
        """Verify 'About' sidebar link points to the official Sauce Labs website."""
        authenticated_page.header.open_sidebar_menu()
        about_url = authenticated_page.sidebar.get_about_url()
        assert "saucelabs.com" in about_url

    def test_all_items_navigation_from_cart(
        self, authenticated_page: InventoryPage, cart_page: CartPage
    ):
        """Verify 'All Items' sidebar option navigates from cart back to inventory."""
        authenticated_page.header.click_shopping_cart()
        authenticated_page.wait_for_url_contains("/cart.html")

        cart_page.header.open_sidebar_menu()
        cart_page.sidebar.click_all_items()
        cart_page.wait_for_url_contains("/inventory.html")
        assert authenticated_page.is_loaded()

    def test_reset_app_state_clears_cart_and_buttons(self, authenticated_page: InventoryPage):
        """Verify 'Reset App State' clears cart badge and restores Add to cart buttons."""
        item = TestData.PRODUCTS[0].name
        authenticated_page.add_product_to_cart(item)
        assert authenticated_page.header.get_cart_badge_count() == 1
        assert authenticated_page.is_remove_button_displayed(item)

        # Open sidebar and reset app state
        authenticated_page.header.open_sidebar_menu()
        authenticated_page.sidebar.click_reset_app_state()

        # Badge should now disappear immediately
        assert not authenticated_page.header.is_cart_badge_visible()

        # Reloading ensures catalog components reflect cleared state
        authenticated_page.reload()
        assert authenticated_page.is_add_to_cart_button_displayed(item)

    def test_logout_navigates_to_login_page(
        self, authenticated_page: InventoryPage, login_page: LoginPage
    ):
        """Verify Logout returns user to the login screen."""
        authenticated_page.header.open_sidebar_menu()
        authenticated_page.sidebar.click_logout()
        assert login_page.is_login_button_visible()
