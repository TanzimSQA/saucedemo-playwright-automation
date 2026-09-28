import os
import sys
import platform
import base64
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from dotenv import load_dotenv

# Ensure workspace root is in python path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.product_details_page import ProductDetailsPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from data.test_data import TestData
from utils.report_generator import generate_html_report

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL", TestData.BASE_URL)
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "15000"))
SLOW_MO = int(os.getenv("SLOW_MO", "0" if HEADLESS else "200"))

SCREENSHOTS_DIR = Path("reports/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Global accumulator for test execution records across the test session
_test_results = {}


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
    request.node._playwright_page = page

    # Network activity tracker initialized early so list reference is available immediately
    network_entries = []
    request.node._network_entries = network_entries

    def on_response(response):
        try:
            req = response.request
            network_entries.append({
                "method": req.method,
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
                "resource_type": req.resource_type,
                "ok": response.ok,
            })
        except Exception:
            pass

    def on_request_failed(request_obj):
        try:
            network_entries.append({
                "method": request_obj.method,
                "url": request_obj.url,
                "status": 0,
                "status_text": request_obj.failure or "Network Failed",
                "resource_type": request_obj.resource_type,
                "ok": False,
            })
        except Exception:
            pass

    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    yield page

    # Screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name.replace("/", "_").replace("::", "_")
        screenshot_path = SCREENSHOTS_DIR / f"failure_{test_name}.png"
        try:
            if not page.is_closed():
                img_bytes = page.screenshot(full_page=True)
                screenshot_path.write_bytes(img_bytes)
                request.node._screenshot_b64 = base64.b64encode(img_bytes).decode("utf-8")
                request.node._screenshot_path = str(screenshot_path)
                if request.node.nodeid in _test_results:
                    _test_results[request.node.nodeid]["screenshot_b64"] = request.node._screenshot_b64
                    _test_results[request.node.nodeid]["screenshot_path"] = str(screenshot_path)
        except Exception:
            pass

    page.close()


@pytest.fixture(scope="function")
def attach_screenshot(request):
    """Fixture enabling tests to capture and embed a visual state or bug screenshot."""
    def _capture(page: Page, title: str = "screenshot"):
        try:
            if not page.is_closed():
                img_bytes = page.screenshot(full_page=True)
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                request.node._screenshot_b64 = b64
                clean_test = request.node.name.replace("/", "_").replace("::", "_")
                path = SCREENSHOTS_DIR / f"{title}_{clean_test}.png"
                path.write_bytes(img_bytes)
                request.node._screenshot_path = str(path)
        except Exception as e:
            print(f"Error capturing test screenshot: {e}")
    return _capture


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hooks into test report generation to capture failures, screenshots, and logs."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # If call failed, take screenshot immediately while page is still alive
    if rep.when == "call" and rep.failed:
        page = getattr(item, "_playwright_page", None)
        if page and not getattr(item, "_screenshot_b64", None):
            try:
                if not page.is_closed():
                    img_bytes = page.screenshot(full_page=True)
                    test_name = item.name.replace("/", "_").replace("::", "_")
                    screenshot_path = SCREENSHOTS_DIR / f"failure_{test_name}.png"
                    screenshot_path.write_bytes(img_bytes)
                    item._screenshot_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    item._screenshot_path = str(screenshot_path)
            except Exception:
                pass

    # Also integrate with pytest-html extras if loaded
    try:
        from pytest_html import extras
        if not hasattr(rep, "extras"):
            rep.extras = []
        if rep.when == "call":
            b64 = getattr(item, "_screenshot_b64", None)
            if b64:
                rep.extras.append(extras.image(b64, "Bug Screenshot"))
    except Exception:
        pass

    # Record data on call completion or on setup failure
    if rep.when == "call" or (rep.when == "setup" and rep.failed):
        nodeid = rep.nodeid
        doc = item.function.__doc__ if hasattr(item, "function") and item.function.__doc__ else ""
        markers = [m.name for m in item.iter_markers() if m.name not in ["parametrize", "filterwarnings"]]
        params = item.callspec.params if hasattr(item, "callspec") else {}

        error_msg = ""
        stack_trace = ""
        if rep.failed:
            if hasattr(rep.longrepr, "reprcrash"):
                error_msg = str(rep.longrepr.reprcrash.message)
            stack_trace = str(rep.longrepr)

        _test_results[nodeid] = {
            "nodeid": nodeid,
            "name": item.name,
            "module": Path(item.fspath).name if hasattr(item, "fspath") else "",
            "status": rep.outcome.upper(),
            "duration": round(rep.duration, 3),
            "doc": doc.strip() if doc else "",
            "markers": markers,
            "parameters": params,
            "error_message": error_msg,
            "stack_trace": stack_trace,
            "screenshot_b64": getattr(item, "_screenshot_b64", ""),
            "screenshot_path": getattr(item, "_screenshot_path", ""),
            "network_entries": list(getattr(item, "_network_entries", [])),
        }

    # If teardown has completed, do a final sync of screenshots and network calls
    if rep.when == "teardown" and item.nodeid in _test_results:
        b64 = getattr(item, "_screenshot_b64", "")
        if b64:
            _test_results[item.nodeid]["screenshot_b64"] = b64
            _test_results[item.nodeid]["screenshot_path"] = getattr(item, "_screenshot_path", "")
        net = getattr(item, "_network_entries", [])
        if net:
            _test_results[item.nodeid]["network_entries"] = list(net)


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generates the advanced colorful executive HTML report after tests complete."""
    results_list = list(_test_results.values())
    if not results_list:
        return

    import playwright

    metadata = {
        "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S BST"),
        "platform": f"{platform.system()} {platform.release()}",
        "python_version": f"Python {platform.python_version()}",
        "playwright_version": getattr(playwright, "__version__", "1.40+"),
        "base_url": BASE_URL,
    }

    html_path = config.getoption("--html") or "reports/test_report.html"
    out_report = Path(html_path)

    # Write to primary target and ensure both index.html and test_report.html are synchronized
    additional = []
    if out_report.name != "index.html":
        additional.append("reports/index.html")
    if out_report.name != "test_report.html":
        additional.append("reports/test_report.html")

    generate_html_report(
        test_results=results_list,
        metadata=metadata,
        output_path=str(out_report),
        additional_paths=additional,
    )

    terminalreporter.write_sep(
        "=",
        f"✨ High-End Advanced QA Dashboard Generated: {out_report} & reports/index.html",
        bold=True,
        green=True,
    )


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
