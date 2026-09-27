import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from data.test_data import TestData


@pytest.mark.security
class TestSecurityAuth:
    """Test suite covering authentication guardrails and unauthorized direct URL access."""

    @pytest.mark.parametrize(
        "protected_endpoint",
        [
            "/inventory.html",
            "/cart.html",
            "/checkout-step-one.html",
            "/checkout-step-two.html",
            "/checkout-complete.html",
        ],
        ids=[
            "inventory_direct",
            "cart_direct",
            "checkout_one_direct",
            "checkout_two_direct",
            "checkout_complete_direct",
        ]
    )
    def test_unauthenticated_direct_access_prevented(
        self, page: Page, login_page: LoginPage, protected_endpoint
    ):
        """Verify accessing internal pages without authenticating is blocked with error message."""
        page.goto(f"{TestData.BASE_URL}{protected_endpoint}")
        assert login_page.is_error_displayed()
        assert "You can only access" in login_page.get_error_message_text()
