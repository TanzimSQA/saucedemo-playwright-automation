import os
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from dotenv import load_dotenv

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from data.test_data import TestData

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL", TestData.BASE_URL)
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "15000"))
SLOW_MO = int(os.getenv("SLOW_MO", "0" if HEADLESS else "200"))

SCREENSHOTS_DIR = Path("reports/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Browser:
    browser = playwright_instance.chromium.launch(
        headless=HEADLESS,
        slow_mo=SLOW_MO,
        args=["--no-sandbox", "--disable-gpu"]
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        base_url=BASE_URL,
        ignore_https_errors=True
    )
    context.set_default_timeout(DEFAULT_TIMEOUT)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, request) -> Page:
    page = context.new_page()
    yield page

    # Screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name.replace("/", "_").replace("::", "_")
        screenshot_path = SCREENSHOTS_DIR / f"failure_{test_name}.png"
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            pass
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stores test outcome in node for fixture teardown screenshot access."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# Page Object Fixtures
@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture(scope="function")
def inventory_page(page: Page) -> InventoryPage:
    return InventoryPage(page)


@pytest.fixture(scope="function")
def product_details_page(page: Page) -> ProductDetailsPage:
    return ProductDetailsPage(page)


@pytest.fixture(scope="function")
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture(scope="function")
def checkout_step_one_page(page: Page) -> CheckoutStepOnePage:
    return CheckoutStepOnePage(page)


@pytest.fixture(scope="function")
def checkout_step_two_page(page: Page) -> CheckoutStepTwoPage:
    return CheckoutStepTwoPage(page)


@pytest.fixture(scope="function")
def checkout_complete_page(page: Page) -> CheckoutCompletePage:
    return CheckoutCompletePage(page)


@pytest.fixture(scope="function")
def authenticated_page(login_page: LoginPage, inventory_page: InventoryPage) -> InventoryPage:
    """Pre-authenticates with standard_user and lands on inventory page."""
    login_page.load(BASE_URL)
    standard_user = TestData.USERS["STANDARD"]
    login_page.login(standard_user.username, standard_user.password)
    login_page.wait_for_url_contains("/inventory.html")
    assert inventory_page.is_loaded(), "Inventory page failed to load after login"
    return inventory_page
