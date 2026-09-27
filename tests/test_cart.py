import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from data.test_data import TestData


@pytest.mark.cart
class TestCart:
    """Test suite covering the Shopping Cart view and cart item interactions."""

    def test_cart_displays_added_items_accurately(
        self, authenticated_page: InventoryPage, cart_page: CartPage
    ):
        """Verify items added from catalog appear accurately in cart with price and quantity."""
        items_to_add = [TestData.PRODUCTS[0], TestData.PRODUCTS[2]]
        for item in items_to_add:
            authenticated_page.add_product_to_cart(item.name)

        authenticated_page.header.click_shopping_cart()
        authenticated_page.wait_for_url_contains("/cart.html")
        assert cart_page.is_loaded()

        cart_items = cart_page.get_cart_items_info()
        assert len(cart_items) == 2

        cart_names = [ci["name"] for ci in cart_items]
        for item in items_to_add:
            assert item.name in cart_names

    def test_remove_item_from_within_cart(
        self, authenticated_page: InventoryPage, cart_page: CartPage
    ):
        """Verify item can be removed directly from cart and header badge updates."""
        item1 = TestData.PRODUCTS[0].name
        item2 = TestData.PRODUCTS[1].name

        authenticated_page.add_product_to_cart(item1)
        authenticated_page.add_product_to_cart(item2)

        authenticated_page.header.click_shopping_cart()
        assert cart_page.get_cart_item_count() == 2
        assert cart_page.header.get_cart_badge_count() == 2

        # Remove item1
        cart_page.remove_item(item1)
        assert cart_page.get_cart_item_count() == 1
        assert cart_page.header.get_cart_badge_count() == 1

        # Remove item2
        cart_page.remove_item(item2)
        assert cart_page.get_cart_item_count() == 0
        assert not cart_page.header.is_cart_badge_visible()

    def test_continue_shopping_preserves_cart_state(
        self, authenticated_page: InventoryPage, cart_page: CartPage
    ):
        """Verify 'Continue Shopping' button returns to inventory while retaining items in cart."""
        item = TestData.PRODUCTS[0].name
        authenticated_page.add_product_to_cart(item)

        authenticated_page.header.click_shopping_cart()
        cart_page.click_continue_shopping()
        authenticated_page.wait_for_url_contains("/inventory.html")

        # Cart badge still displays 1 and item shows Remove button
        assert authenticated_page.header.get_cart_badge_count() == 1
        assert authenticated_page.is_remove_button_displayed(item)

    def test_proceed_to_checkout_navigation(
        self, authenticated_page: InventoryPage, cart_page: CartPage, checkout_step_one_page: CheckoutStepOnePage
    ):
        """Verify 'Checkout' button navigates to Checkout: Your Information."""
        authenticated_page.add_product_to_cart(TestData.PRODUCTS[0].name)
        authenticated_page.header.click_shopping_cart()
        cart_page.click_checkout()
        cart_page.wait_for_url_contains("/checkout-step-one.html")
        assert checkout_step_one_page.is_loaded()
