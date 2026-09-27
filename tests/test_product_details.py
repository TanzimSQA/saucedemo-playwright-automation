import pytest
from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage
from data.test_data import TestData


@pytest.mark.inventory
class TestProductDetails:
    """Test suite covering the Product Details page."""

    def test_product_details_information_accuracy(
        self, authenticated_page: InventoryPage, product_details_page: ProductDetailsPage
    ):
        """Verify product details display accurate name, description, and price."""
        product = TestData.PRODUCTS[3]  # Fleece Jacket
        authenticated_page.open_product_details_by_name(product.name)
        authenticated_page.wait_for_url_contains("/inventory-item.html")

        assert product_details_page.get_name() == product.name
        assert product.description_snippet in product_details_page.get_description()
        assert product_details_page.get_price() == product.price
        assert product_details_page.product_image.is_visible()

    def test_add_and_remove_from_product_details_page(
        self, authenticated_page: InventoryPage, product_details_page: ProductDetailsPage
    ):
        """Verify adding and removing items directly on the product details page."""
        product = TestData.PRODUCTS[1]  # Bike Light
        authenticated_page.open_product_details_by_name(product.name)

        # Add to cart
        assert product_details_page.is_add_to_cart_displayed()
        product_details_page.add_to_cart()
        assert product_details_page.is_remove_displayed()
        assert product_details_page.header.get_cart_badge_count() == 1

        # Remove from cart
        product_details_page.remove_from_cart()
        assert product_details_page.is_add_to_cart_displayed()
        assert not product_details_page.header.is_cart_badge_visible()

    def test_back_to_products_navigation(
        self, authenticated_page: InventoryPage, product_details_page: ProductDetailsPage
    ):
        """Verify clicking 'Back to products' returns user to inventory catalog."""
        product = TestData.PRODUCTS[0]
        authenticated_page.open_product_details_by_name(product.name)
        product_details_page.back_to_products()
        authenticated_page.wait_for_url_contains("/inventory.html")
        assert authenticated_page.is_loaded()

    def test_cart_state_consistency_between_inventory_and_details(
        self, authenticated_page: InventoryPage, product_details_page: ProductDetailsPage
    ):
        """Verify an item added on the inventory page shows as already added on the details page."""
        product = TestData.PRODUCTS[0]
        authenticated_page.add_product_to_cart(product.name)
        authenticated_page.open_product_details_by_name(product.name)

        # Should show Remove button immediately
        assert product_details_page.is_remove_displayed()
        product_details_page.remove_from_cart()

        # Returning to catalog should now show Add to cart
        product_details_page.back_to_products()
        assert authenticated_page.is_add_to_cart_button_displayed(product.name)
