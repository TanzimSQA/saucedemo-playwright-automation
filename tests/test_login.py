import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from data.test_data import TestData


@pytest.mark.login
class TestLogin:
    """Test suite covering all login scenarios, validations, and edge cases."""

    def test_successful_login_standard_user(self, login_page: LoginPage, inventory_page: InventoryPage):
        """Verify standard user can log in successfully and reaches inventory page."""
        login_page.load()
        user = TestData.USERS["STANDARD"]
        login_page.login(user.username, user.password)
        login_page.wait_for_url_contains("/inventory.html")
        assert inventory_page.is_loaded()
        assert not login_page.is_error_displayed()

    def test_locked_out_user_error(self, login_page: LoginPage):
        """Verify locked out user receives the expected lockout error message."""
        login_page.load()
        user = TestData.USERS["LOCKED_OUT"]
        login_page.login(user.username, user.password)
        assert login_page.is_error_displayed()
        assert login_page.get_error_message_text() == TestData.ERRORS["LOCKED_OUT"]

    @pytest.mark.parametrize(
        "username, password, expected_error",
        [
            ("", "", TestData.ERRORS["EMPTY_USERNAME"]),
            ("", TestData.DEFAULT_PASSWORD, TestData.ERRORS["EMPTY_USERNAME"]),
            (TestData.USERS["STANDARD"].username, "", TestData.ERRORS["EMPTY_PASSWORD"]),
            ("invalid_user", TestData.DEFAULT_PASSWORD, TestData.ERRORS["INVALID_CREDENTIALS"]),
            (TestData.USERS["STANDARD"].username, "wrong_pass", TestData.ERRORS["INVALID_CREDENTIALS"]),
            ("admin' OR '1'='1", "password", TestData.ERRORS["INVALID_CREDENTIALS"]),
        ],
        ids=[
            "empty_both",
            "empty_username_with_password",
            "standard_username_empty_password",
            "invalid_username_valid_password",
            "valid_username_invalid_password",
            "sql_injection_attempt",
        ]
    )
    def test_login_negative_and_validation(self, login_page: LoginPage, username, password, expected_error):
        """Verify error messages for all invalid and empty credential combinations."""
        login_page.load()
        login_page.login(username, password)
        assert login_page.is_error_displayed()
        assert expected_error in login_page.get_error_message_text()

    def test_error_message_dismissal(self, login_page: LoginPage):
        """Verify clicking the 'X' button dismisses the error message banner."""
        login_page.load()
        login_page.login("", "")
        assert login_page.is_error_displayed()
        login_page.dismiss_error()
        assert not login_page.is_error_displayed()

    def test_password_field_is_masked(self, login_page: LoginPage):
        """Verify password input field has type='password' to mask sensitive text."""
        login_page.load()
        assert login_page.password_input.get_attribute("type") == "password"

    def test_credential_helpers_displayed(self, login_page: LoginPage):
        """Verify demo credential helpers are visible on login screen."""
        login_page.load()
        assert login_page.login_credentials_container.is_visible()
        assert login_page.login_password_container.is_visible()
