"""Page Object Model (POM) package."""
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage

__all__ = [
    "BasePage",
    "LoginPage",
    "InventoryPage",
    "ProductDetailsPage",
    "CartPage",
    "CheckoutStepOnePage",
    "CheckoutStepTwoPage",
    "CheckoutCompletePage",
]
