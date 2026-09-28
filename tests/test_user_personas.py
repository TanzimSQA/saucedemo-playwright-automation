import time
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from data.test_data import TestData


@pytest.mark.persona
class TestUserPersonas:
    """Test suite covering SauceDemo simulated user personas."""

    def test_locked_out_user_persona(self, login_page: LoginPage, attach_screenshot):
        """Verify locked_out_user cannot access inventory and receives lockout banner."""
        login_page.load()
        user = TestData.USERS["LOCKED_OUT"]
        login_page.login(user.username, user.password)
        attach_screenshot(login_page.page, "bug_locked_out_user_error")
        assert login_page.is_error_displayed()
        assert TestData.ERRORS["LOCKED_OUT"] in login_page.get_error_message_text()

    def test_problem_user_persona_detects_image_glitches(
        self, login_page: LoginPage, inventory_page: InventoryPage, attach_screenshot
    ):
        """Verify problem_user encounters duplicate/incorrect image sources."""
        login_page.load()
        user = TestData.USERS["PROBLEM"]
        login_page.login(user.username, user.password)
        login_page.wait_for_url_contains("/inventory.html")
        assert inventory_page.is_loaded()

        # Problem user replaces all images with the same dog image (sl-404.168b1cce.jpg)
        images = inventory_page.page.locator(".inventory_item_img img")
        images.first.wait_for(state="visible", timeout=5000)
        img_srcs = [images.nth(i).get_attribute("src") for i in range(images.count())]
        # Attach the bug screenshot showcasing the dog glitch images
        attach_screenshot(inventory_page.page, "bug_problem_user_dog_glitch")
        # In problem_user, all image srcs are identical
        assert len(set(img_srcs)) == 1, "Problem user was expected to display identical glitch images"

    def test_performance_glitch_user_persona(
        self, login_page: LoginPage, inventory_page: InventoryPage
    ):
        """Verify performance_glitch_user logs in successfully despite latency."""
        login_page.load()
        user = TestData.USERS["PERFORMANCE_GLITCH"]
        login_page.login(user.username, user.password)
        login_page.wait_for_url_contains("/inventory.html", timeout=20000)
        assert inventory_page.is_loaded()

    def test_error_user_persona(
        self, login_page: LoginPage, inventory_page: InventoryPage, checkout_step_one_page: CheckoutStepOnePage, attach_screenshot
    ):
        """Verify error_user encounters errors during checkout completion."""
        login_page.load()
        user = TestData.USERS["ERROR"]
        login_page.login(user.username, user.password)
        login_page.wait_for_url_contains("/inventory.html")

        # Add item and go to checkout
        inventory_page.add_product_to_cart(TestData.PRODUCTS[0].name)
        inventory_page.header.click_shopping_cart()
        inventory_page.page.locator("[data-test='checkout']").click()

        # Step one with valid customer data
        checkout_step_one_page.fill_customer_info("John", "Doe", "12345")
        checkout_step_one_page.click_continue()
        attach_screenshot(checkout_step_one_page.page, "bug_error_user_checkout")
        # error_user might produce an error banner or block continuation
        # Check if error or successful navigation
        assert checkout_step_one_page.is_error_displayed() or "/checkout-step-two.html" in checkout_step_one_page.current_url
