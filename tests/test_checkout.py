import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from data.test_data import TestData
from utils.helpers import calculate_tax


@pytest.mark.checkout
class TestCheckout:
    """Test suite covering the 3-step checkout flow, data validations, and calculations."""

    @pytest.fixture(autouse=True)
    def setup_cart_and_navigate_to_checkout(
        self, authenticated_page: InventoryPage, cart_page: CartPage, checkout_step_one_page: CheckoutStepOnePage
    ):
        """Helper to seed cart and enter checkout step one before each test."""
        self.item = TestData.PRODUCTS[0]
        authenticated_page.add_product_to_cart(self.item.name)
        authenticated_page.header.click_shopping_cart()
        cart_page.click_checkout()
        checkout_step_one_page.wait_for_url_contains("/checkout-step-one.html")

    @pytest.mark.parametrize(
        "first_name, last_name, postal_code, expected_error",
        [
            ("", "Doe", "12345", TestData.ERRORS["FIRST_NAME_REQUIRED"]),
            ("John", "", "12345", TestData.ERRORS["LAST_NAME_REQUIRED"]),
            ("John", "Doe", "", TestData.ERRORS["POSTAL_CODE_REQUIRED"]),
            ("", "", "", TestData.ERRORS["FIRST_NAME_REQUIRED"]),
        ],
        ids=["missing_first_name", "missing_last_name", "missing_postal_code", "missing_all_fields"]
    )
    def test_checkout_step_one_validations(
        self, checkout_step_one_page: CheckoutStepOnePage, first_name, last_name, postal_code, expected_error
    ):
        """Verify field validation errors on checkout step one."""
        checkout_step_one_page.fill_customer_info(first_name, last_name, postal_code)
        checkout_step_one_page.click_continue()
        assert checkout_step_one_page.is_error_displayed()
        assert checkout_step_one_page.get_error_message() == expected_error

    def test_checkout_step_one_dismiss_error(self, checkout_step_one_page: CheckoutStepOnePage):
        """Verify closing the error message banner on checkout step one."""
        checkout_step_one_page.click_continue()
        assert checkout_step_one_page.is_error_displayed()
        checkout_step_one_page.dismiss_error()
        assert not checkout_step_one_page.is_error_displayed()

    def test_checkout_step_one_cancel_button(
        self, checkout_step_one_page: CheckoutStepOnePage, cart_page: CartPage
    ):
        """Verify clicking Cancel on step one returns user to the cart page."""
        checkout_step_one_page.click_cancel()
        checkout_step_one_page.wait_for_url_contains("/cart.html")
        assert cart_page.is_loaded()

    def test_checkout_step_two_financial_calculations_and_content(
        self,
        checkout_step_one_page: CheckoutStepOnePage,
        checkout_step_two_page: CheckoutStepTwoPage
    ):
        """Verify order summary, prices, tax calculation, and total on step two."""
        customer = TestData.VALID_CUSTOMER
        checkout_step_one_page.fill_customer_info(
            customer.first_name, customer.last_name, customer.postal_code
        )
        checkout_step_one_page.click_continue()
        checkout_step_one_page.wait_for_url_contains("/checkout-step-two.html")
        assert checkout_step_two_page.is_loaded()

        # Item verification
        item_names = checkout_step_two_page.get_item_names()
        assert self.item.name in item_names

        # Subtotal calculation
        subtotal = checkout_step_two_page.get_subtotal()
        assert subtotal == self.item.price

        # Tax and total calculation
        tax = checkout_step_two_page.get_tax()
        total = checkout_step_two_page.get_total()
        expected_tax = calculate_tax(subtotal)
        assert abs(tax - expected_tax) <= 0.02  # allow rounding tolerance
        assert round(subtotal + tax, 2) == round(total, 2)

        # Shipping and payment info
        assert "SauceCard" in checkout_step_two_page.get_payment_info()
        assert "Pony Express" in checkout_step_two_page.get_shipping_info()

    def test_checkout_step_two_cancel_button(
        self,
        checkout_step_one_page: CheckoutStepOnePage,
        checkout_step_two_page: CheckoutStepTwoPage,
        inventory_page: InventoryPage
    ):
        """Verify clicking Cancel on step two returns user to the inventory page."""
        customer = TestData.VALID_CUSTOMER
        checkout_step_one_page.fill_customer_info(
            customer.first_name, customer.last_name, customer.postal_code
        )
        checkout_step_one_page.click_continue()
        checkout_step_two_page.click_cancel()
        checkout_step_two_page.wait_for_url_contains("/inventory.html")
        assert inventory_page.is_loaded()

    def test_checkout_complete_and_back_home(
        self,
        checkout_step_one_page: CheckoutStepOnePage,
        checkout_step_two_page: CheckoutStepTwoPage,
        checkout_complete_page: CheckoutCompletePage,
        inventory_page: InventoryPage
    ):
        """Verify complete purchase order flow and return to home resets cart."""
        customer = TestData.VALID_CUSTOMER
        checkout_step_one_page.fill_customer_info(
            customer.first_name, customer.last_name, customer.postal_code
        )
        checkout_step_one_page.click_continue()
        checkout_step_two_page.click_finish()
        checkout_two_wait = checkout_two_page = checkout_step_two_page
        checkout_two_wait.wait_for_url_contains("/checkout-complete.html")

        # Verify completion confirmation
        assert checkout_complete_page.is_loaded()
        assert checkout_complete_page.get_order_complete_header() == TestData.CHECKOUT_SUCCESS["HEADER"]
        assert TestData.CHECKOUT_SUCCESS["TEXT"] in checkout_complete_page.get_order_complete_text()
        assert checkout_complete_page.is_pony_express_image_visible()

        # Cart badge must be cleared
        assert not checkout_complete_page.header.is_cart_badge_visible()

        # Click back home
        checkout_complete_page.click_back_home()
        checkout_complete_page.wait_for_url_contains("/inventory.html")
        assert inventory_page.is_loaded()
        assert not inventory_page.header.is_cart_badge_visible()
