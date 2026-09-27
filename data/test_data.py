"""
Comprehensive test data and constants for SauceDemo automated tests.
"""

from typing import Dict, List, NamedTuple


class UserCredentials(NamedTuple):
    username: str
    password: str


class CustomerInfo(NamedTuple):
    first_name: str
    last_name: str
    postal_code: str


class ProductInfo(NamedTuple):
    name: str
    price: float
    description_snippet: str


class TestData:
    BASE_URL = "https://www.saucedemo.com"
    DEFAULT_PASSWORD = "secret_sauce"

    # User Accounts
    USERS = {
        "STANDARD": UserCredentials("standard_user", DEFAULT_PASSWORD),
        "LOCKED_OUT": UserCredentials("locked_out_user", DEFAULT_PASSWORD),
        "PROBLEM": UserCredentials("problem_user", DEFAULT_PASSWORD),
        "PERFORMANCE_GLITCH": UserCredentials("performance_glitch_user", DEFAULT_PASSWORD),
        "ERROR": UserCredentials("error_user", DEFAULT_PASSWORD),
        "VISUAL": UserCredentials("visual_user", DEFAULT_PASSWORD),
        "INVALID": UserCredentials("non_existent_user", "invalid_password"),
        "EMPTY": UserCredentials("", ""),
    }

    # Error Messages
    ERRORS = {
        "EMPTY_USERNAME": "Epic sadface: Username is required",
        "EMPTY_PASSWORD": "Epic sadface: Password is required",
        "LOCKED_OUT": "Epic sadface: Sorry, this user has been locked out.",
        "INVALID_CREDENTIALS": "Epic sadface: Username and password do not match any user in this service",
        "FIRST_NAME_REQUIRED": "Error: First Name is required",
        "LAST_NAME_REQUIRED": "Error: Last Name is required",
        "POSTAL_CODE_REQUIRED": "Error: Postal Code is required",
        "UNAUTHORIZED_ACCESS": "Epic sadface: You can only access '/inventory.html' when you are logged in.",
    }

    # Catalog Products
    PRODUCTS: List[ProductInfo] = [
        ProductInfo("Sauce Labs Backpack", 29.99, "carry.allTheThings() with the sleek, streamlined Sly Pack"),
        ProductInfo("Sauce Labs Bike Light", 9.99, "A red light isn't the desired state in testing but it is with this light"),
        ProductInfo("Sauce Labs Bolt T-Shirt", 15.99, "Get your testing superhero on with the Sauce Labs bolt T-shirt"),
        ProductInfo("Sauce Labs Fleece Jacket", 49.99, "It's not every day that you come across a midweight quarter-zip fleece jacket"),
        ProductInfo("Sauce Labs Onesie", 7.99, "Rib snaps at the bottom for easy dressing and diaper changes"),
        ProductInfo("Test.allTheThings() T-Shirt (Red)", 15.99, "This classic Sauce Labs t-shirt is perfect to wear when cozying up to your keyboard"),
    ]

    # Checkout Datasets
    VALID_CUSTOMER = CustomerInfo(
        first_name="John",
        last_name="Doe",
        postal_code="94103"
    )

    INCOMPLETE_CUSTOMERS = [
        {"info": CustomerInfo("", "Doe", "94103"), "expected_error": "Error: First Name is required"},
        {"info": CustomerInfo("John", "", "94103"), "expected_error": "Error: Last Name is required"},
        {"info": CustomerInfo("John", "Doe", ""), "expected_error": "Error: Postal Code is required"},
        {"info": CustomerInfo("", "", ""), "expected_error": "Error: First Name is required"},
    ]

    # Checkout Confirmation
    CHECKOUT_SUCCESS = {
        "HEADER": "Thank you for your order!",
        "TEXT": "Your order has been dispatched, and will arrive just as fast as the pony can get there!",
    }

    # Sorting options
    SORT_OPTIONS = {
        "A_TO_Z": "az",
        "Z_TO_A": "za",
        "LOW_TO_HIGH": "lohi",
        "HIGH_TO_LOW": "hilo",
    }

    # Footer social links
    SOCIAL_LINKS = {
        "x": "x.com/saucelabs",
        "twitter": "x.com/saucelabs",
        "facebook": "facebook.com/saucelabs",
        "linkedin": "linkedin.com/company/sauce-labs",
    }
