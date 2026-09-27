import pytest
from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage
from data.test_data import TestData


@pytest.mark.inventory
class TestInventory:
    """Test suite covering inventory catalog, sorting, and item card actions."""

    def test_catalog_displays_all_default_products(self, authenticated_page: InventoryPage):
        """Verify all standard products are displayed in the catalog."""
        product_names = authenticated_page.get_product_names()
        assert len(product_names) == 6
        expected_names = [p.name for p in TestData.PRODUCTS]
        assert set(product_names) == set(expected_names)

    def test_sort_name_a_to_z(self, authenticated_page: InventoryPage):
        """Verify sorting by Name (A to Z)."""
        authenticated_page.select_sort_option(TestData.SORT_OPTIONS["A_TO_Z"])
        names = authenticated_page.get_product_names()
        assert names == sorted(names), "Products are not sorted alphabetically (A to Z)"

    def test_sort_name_z_to_a(self, authenticated_page: InventoryPage):
        """Verify sorting by Name (Z to A)."""
        authenticated_page.select_sort_option(TestData.SORT_OPTIONS["Z_TO_A"])
        names = authenticated_page.get_product_names()
        assert names == sorted(names, reverse=True), "Products are not sorted in reverse alphabetical order (Z to A)"

    def test_sort_price_low_to_high(self, authenticated_page: InventoryPage):
        """Verify sorting by Price (low to high)."""
        authenticated_page.select_sort_option(TestData.SORT_OPTIONS["LOW_TO_HIGH"])
        prices = authenticated_page.get_product_prices()
        assert prices == sorted(prices), "Prices are not sorted from low to high"

    def test_sort_price_high_to_low(self, authenticated_page: InventoryPage):
        """Verify sorting by Price (high to low)."""
        authenticated_page.select_sort_option(TestData.SORT_OPTIONS["HIGH_TO_LOW"])
        prices = authenticated_page.get_product_prices()
        assert prices == sorted(prices, reverse=True), "Prices are not sorted from high to low"

    def test_add_and_remove_item_cart_badge_updates(self, authenticated_page: InventoryPage):
        """Verify adding and removing items properly updates button state and shopping cart badge."""
        item = TestData.PRODUCTS[0].name

        # Initial state: badge not visible
        assert not authenticated_page.header.is_cart_badge_visible()

        # Add item
        authenticated_page.add_product_to_cart(item)
        assert authenticated_page.is_remove_button_displayed(item)
        assert authenticated_page.header.get_cart_badge_count() == 1

        # Add second item
        item2 = TestData.PRODUCTS[1].name
        authenticated_page.add_product_to_cart(item2)
        assert authenticated_page.header.get_cart_badge_count() == 2

        # Remove first item
        authenticated_page.remove_product_from_cart(item)
        assert authenticated_page.is_add_to_cart_button_displayed(item)
        assert authenticated_page.header.get_cart_badge_count() == 1

        # Remove second item
        authenticated_page.remove_product_from_cart(item2)
        assert not authenticated_page.header.is_cart_badge_visible()

    def test_navigate_to_product_details_via_title(
        self, authenticated_page: InventoryPage, product_details_page: ProductDetailsPage
    ):
        """Verify clicking product title opens correct details page."""
        target_item = TestData.PRODUCTS[0]
        authenticated_page.open_product_details_by_name(target_item.name)
        authenticated_page.wait_for_url_contains("/inventory-item.html")
        assert product_details_page.get_name() == target_item.name
        assert product_details_page.get_price() == target_item.price

    def test_navigate_to_product_details_via_image(
        self, authenticated_page: InventoryPage, product_details_page: ProductDetailsPage
    ):
        """Verify clicking product image opens details page."""
        target_item = TestData.PRODUCTS[2]
        authenticated_page.open_product_details_by_image(target_item.name)
        authenticated_page.wait_for_url_contains("/inventory-item.html")
        assert product_details_page.get_name() == target_item.name
