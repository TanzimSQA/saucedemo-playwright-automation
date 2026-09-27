# SauceDemo Enterprise Automation Testing Framework

[![SauceDemo Playwright Test Automation CI/CD](https://github.com/TanzimSQA/saucedemo-playwright-automation/actions/workflows/playwright_ci.yml/badge.svg)](https://github.com/TanzimSQA/saucedemo-playwright-automation/actions/workflows/playwright_ci.yml)
[![GitHub Pages Report](https://img.shields.io/badge/Test%20Report-GitHub%20Pages-brightgreen?style=flat&logo=github)](https://tanzimsqa.github.io/saucedemo-playwright-automation/)
[![Schedule](https://img.shields.io/badge/Scheduled%20Run-10%3A00%20AM%20BST%20Everyday-blue)](https://github.com/TanzimSQA/saucedemo-playwright-automation/actions)

An enterprise-grade, end-to-end automated testing suite for [SauceDemo (Swag Labs)](https://www.saucedemo.com/) developed with **Python**, **Playwright**, and **Pytest**, following the industry-standard **Page Object Model (POM)** pattern.

> 🌐 **Live Interactive HTML Test Report**: [https://tanzimsqa.github.io/saucedemo-playwright-automation/](https://tanzimsqa.github.io/saucedemo-playwright-automation/)  
> ⏰ **Automated Schedule**: Runs automatically every day at **10:00 AM Bangladesh Standard Time (BST, UTC+6)** / `04:00 UTC`.

---

## 🚀 Key Framework Features

- **Page Object Model (POM)**: Complete separation between UI locators/actions and test logic.
- **100% Feature & Sub-feature Coverage**:
  - **Authentication & Security**: Valid credentials, locked out user, invalid users, empty fields, masked passwords, credential helper boxes, and unauthorized route access prevention.
  - **Product Catalog & Inventory**: All 6 default catalog items, image links, title links, price assertions, and cart badge dynamic count updates (+/-).
  - **Multi-criteria Sorting Permutations**:
    - Name (A to Z)
    - Name (Z to A)
    - Price (Low to High)
    - Price (High to Low)
  - **Product Details**: Deep product view, item descriptions, price verification, add/remove synchronization with catalog.
  - **Shopping Cart**: Item quantity, item descriptions, price integrity, item deletion, badge synchronization, and "Continue Shopping" persistence.
  - **3-Step Checkout Flow**:
    - **Step 1 (Information)**: First name, last name, postal code validations (missing first, missing last, missing zip, missing all), dismissible error banners, and cancel routing.
    - **Step 2 (Overview)**: Summary line items, payment info (SauceCard), shipping info (Pony Express), automated subtotal math verification, dynamic 8% tax calculation, and cancel routing.
    - **Step 3 (Complete)**: Order dispatch confirmation, pony express graphics, and automatic cart reset upon returning home.
  - **Sidebar & Hamburger Menu**: All Items routing, external Sauce Labs About URL verification, Reset App State, and secure Logout.
  - **Footer & Social Links**: X (Twitter), Facebook, and LinkedIn links opening in new tabs (`target="_blank"`), plus copyright statements.
  - **User Personas**: Simulated user behavior tests for `standard_user`, `locked_out_user`, `problem_user` (broken images detection), `performance_glitch_user` (high latency tolerance), and `error_user`.
- **Automated HTML Reporting**: Generates interactive test execution reports via `pytest-html`.
- **Automatic Failure Screenshots**: Automatically captures and stores full-page screenshots under `reports/screenshots/` upon test failure.

---

## 📁 Project Architecture

```
D:\Automation testing\
├── .env                              # Environment configuration (Base URL, headless mode, timeouts)
├── pytest.ini                        # Pytest configuration, test discovery, markers, and report opts
├── requirements.txt                  # Python dependencies
├── README.md                         # Framework documentation
├── data/
│   ├── __init__.py
│   └── test_data.py                  # Test datasets, users, errors, products, checkout models
├── pages/
│   ├── __init__.py                   # Page exports
│   ├── base_page.py                  # Base page wrapper with Playwright waits & actions
│   ├── login_page.py                 # Login Page Object
│   ├── inventory_page.py             # Inventory / Products Catalog Page Object
│   ├── product_details_page.py       # Product Details Page Object
│   ├── cart_page.py                  # Shopping Cart Page Object
│   ├── checkout_step_one_page.py     # Checkout: Information Page Object
│   ├── checkout_step_two_page.py     # Checkout: Overview Page Object
│   ├── checkout_complete_page.py     # Checkout: Complete Page Object
│   └── components/
│       ├── __init__.py
│       ├── header_component.py       # App logo, cart badge, menu button
│       ├── sidebar_component.py      # Hamburger navigation drawer & reset state
│       └── footer_component.py       # Social media links & copyright
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures, browser lifecycle & failure hooks
│   ├── test_login.py                 # 11 Authentication & validation test cases
│   ├── test_inventory.py             # 8 Catalog, sorting, and cart badge test cases
│   ├── test_product_details.py       # 4 Product detail view & sync test cases
│   ├── test_cart.py                  # 4 Shopping cart interaction test cases
│   ├── test_checkout.py              # 9 Comprehensive checkout flow & math test cases
│   ├── test_end_to_end.py            # 2 Complete multi-step buyer journey test cases
│   ├── test_sidebar_navigation.py    # 5 Sidebar drawer, state reset & logout test cases
│   ├── test_footer_social.py         # 4 Social links & copyright test cases
│   ├── test_security_auth.py         # 5 Unauthenticated route guardrail test cases
│   └── test_user_personas.py         # 4 User persona & edge-case test cases
├── utils/
│   ├── __init__.py
│   └── helpers.py                    # Currency parsers & tax calculation utilities
└── reports/
    ├── test_report.html              # Standalone interactive test execution report
    └── screenshots/                  # Failure screenshots capture directory
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.14)
- Google Chrome / Chromium

### 2. Activate Virtual Environment & Install Dependencies

```powershell
# In D:\Automation testing
.\venv\Scripts\Activate.ps1

# Install requirements
python -m pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

---

## 🧪 Running the Tests

### Run All 56 Test Cases
```powershell
python -m pytest
```

### Run Tests in Headed Mode (Watch Browser UI)
Modify `.env` to set `HEADLESS=false` or run:
```powershell
python -m pytest -o "addopts=-v -s --headed"
```

### Run by Test Categories (Markers)
```powershell
# Run Smoke / Happy path tests
python -m pytest -m smoke

# Run Login & Authentication tests
python -m pytest -m login

# Run Inventory & Sorting tests
python -m pytest -m inventory

# Run Cart tests
python -m pytest -m cart

# Run Checkout tests
python -m pytest -m checkout

# Run End-to-End User Journeys
python -m pytest -m e2e

# Run Security & Authorization tests
python -m pytest -m security

# Run User Persona tests
python -m pytest -m persona
```

### Run Specific Test Modules
```powershell
python -m pytest tests/test_login.py -v
python -m pytest tests/test_checkout.py -v
python -m pytest tests/test_end_to_end.py -v
```

---

## 📊 Test Reports & Logs

After running the tests, an interactive HTML report is automatically generated at:
```
D:\Automation testing\reports\test_report.html
```

To view the report in your default browser:
```powershell
Start-Process "D:\Automation testing\reports\test_report.html"
```

If any test fails, a full-page screenshot is automatically recorded in:
```
D:\Automation testing\reports\screenshots/
```
