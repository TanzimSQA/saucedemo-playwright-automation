import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from data.test_data import TestData


@pytest.mark.e2e
@pytest.mark.smoke
class TestEndToEnd:
    """Comprehensive End-to-End User Journey Tests."""

    def test_e2e_single_item_complete_purchase(
        self,
        login_page: LoginPage,
        inventory_page: InventoryPage,
        cart_page: CartPage,
        checkout_step_one_page: CheckoutStepOnePage,
        checkout_step_two_page: CheckoutStepTwoPage,
        checkout_complete_page: CheckoutCompletePage
    ):
        """E2E Journey: Login -> Add Product -> Cart -> Checkout 1 -> Checkout 2 -> Finish -> Logout."""
        # 1. Login
        login_page.load()
        standard_user = TestData.USERS["STANDARD"]
        login_page.login(standard_user.username, standard_user.password)
        login_page.wait_for_url_contains("/inventory.html")
        assert inventory_page.is_loaded()

        # 2. Add product
        selected_product = TestData.PRODUCTS[0]  # Backpack
        inventory_page.add_product_to_cart(selected_product.name)
        assert inventory_page.header.get_cart_badge_count() == 1

        # 3. View Cart
        inventory_page.header.click_shopping_cart()
        inventory_page.wait_for_url_contains("/cart.html")
        assert cart_page.is_loaded()
        assert cart_page.get_cart_item_count() == 1

        # 4. Checkout Step One
        cart_page.click_checkout()
        cart_page.wait_for_url_contains("/checkout-step-one.html")
        customer = TestData.VALID_CUSTOMER
        checkout_step_one_page.fill_customer_info(customer.first_name, customer.last_name, customer.postal_code)
        checkout_step_one_page.click_continue()

        # 5. Checkout Step Two (Overview)
        checkout_step_one_page.wait_for_url_contains("/checkout-step-two.html")
        assert checkout_step_two_page.is_loaded()
        assert checkout_step_two_page.get_subtotal() == selected_product.price
        checkout_step_two_page.click_finish()

        # 6. Checkout Complete
        checkout_step_two_page.wait_for_url_contains("/checkout-complete.html")
        assert checkout_complete_page.is_loaded()
        assert checkout_complete_page.get_order_complete_header() == TestData.CHECKOUT_SUCCESS["HEADER"]

        # 7. Return to Inventory & Logout
        checkout_complete_page.click_back_home()
        checkout_complete_page.wait_for_url_contains("/inventory.html")
        inventory_page.header.open_sidebar_menu()
        inventory_page.sidebar.click_logout()
        assert login_page.is_login_button_visible()

    def test_e2e_multiple_items_purchase_with_sorting(
        self,
        authenticated_page: InventoryPage,
        cart_page: CartPage,
        checkout_step_one_page: CheckoutStepOnePage,
        checkout_step_two_page: CheckoutStepTwoPage,
        checkout_complete_page: CheckoutCompletePage
    ):
        """E2E Journey: Sort by price -> Add lowest and highest items -> Verify cart -> Checkout."""
        # Sort price high to low
        authenticated_page.select_sort_option(TestData.SORT_OPTIONS["HIGH_TO_LOW"])
        sorted_names = authenticated_page.get_product_names()

        highest_item = sorted_names[0]
        lowest_item = sorted_names[-1]

        # Add both to cart
        authenticated_page.add_product_to_cart(highest_item)
        authenticated_page.add_product_to_cart(lowest_item)
        assert authenticated_page.header.get_cart_badge_count() == 2

        # Open Cart
        authenticated_page.header.click_shopping_cart()
        authenticated_page.wait_for_url_contains("/cart.html")
        assert cart_page.is_loaded()
        assert cart_page.get_cart_item_count() == 2

        # Proceed to Checkout
        cart_page.click_checkout()
        customer = TestData.VALID_CUSTOMER
        checkout_step_one_page.fill_customer_info(customer.first_name, customer.last_name, customer.postal_code)
        checkout_step_one_page.click_continue()

        # Step Two - Verify overview totals
        assert checkout_step_two_page.is_loaded()
        items_in_overview = checkout_step_two_page.get_item_names()
        assert highest_item in items_in_overview
        assert lowest_item in items_in_overview

        subtotal = checkout_step_two_page.get_subtotal()
        prices = checkout_step_two_page.get_item_prices()
        assert subtotal == sum(prices)

        # Complete Order
        checkout_step_two_page.click_finish()
        assert checkout_complete_page.is_loaded()
