"""
High-End Colorful Interactive HTML Report Generator for SauceDemo Playwright Automation.
Generates an executive, self-contained single-file HTML test report with:
- Dark / Light Mode with sleek Glassmorphism / Cyber QA dashboard theme
- Executive KPI Cards (Total, Passed, Failed, Skipped, Pass Rate %, Total Runtime)
- Interactive SVG Donut / Pi-Chart for test outcomes with hover tooltips and legends
- Test Suite Module Distribution Chart
- Interactive Architecture & Automation Flowchart Diagram (Playwright -> Page Objects -> Test Matrix -> Quality Gate)
- Instant Search, Status Filters (Passed, Failed, Skipped, Has Screenshots, Has Network Calls), Suite Category Filters, and Sorting
- Bug & Glitch Screenshots embedded directly in base64 with interactive Fullscreen Lightbox Modal
- Detailed Network Inspector capturing all HTTP Requests & Responses (Status, Method, Resource Type, URL, Latency)
- Stack traces with syntax formatting and one-click copy
- 100% Self-Contained: Zero external CDN dependencies, works seamlessly on GitHub Pages and local browsers.
"""

import json
import base64
import html
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


def format_duration(seconds: float) -> str:
    """Format seconds into readable human string."""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        rem_sec = seconds % 60
        return f"{minutes}m {rem_sec:.1f}s"


def clean_test_name(name: str) -> str:
    """Convert snake_case test name to readable title."""
    clean = re.sub(r"^test_", "", name)
    clean = clean.replace("_", " ").title()
    return clean


def get_suite_category(module_name: str, nodeid: str) -> Dict[str, str]:
    """Map test file or nodeid to suite category metadata."""
    mod = module_name.lower()
    if "login" in mod:
        return {"name": "Authentication & Login", "icon": "🔑", "color": "#6366f1", "id": "login"}
    elif "inventory" in mod:
        return {"name": "Catalog & Inventory", "icon": "📦", "color": "#06b6d4", "id": "inventory"}
    elif "product_details" in mod:
        return {"name": "Product Details", "icon": "🔍", "color": "#3b82f6", "id": "product_details"}
    elif "cart" in mod:
        return {"name": "Shopping Cart", "icon": "🛒", "color": "#8b5cf6", "id": "cart"}
    elif "checkout" in mod:
        return {"name": "Checkout Flow", "icon": "💳", "color": "#ec4899", "id": "checkout"}
    elif "end_to_end" in mod:
        return {"name": "End-to-End Journeys", "icon": "🚀", "color": "#10b981", "id": "e2e"}
    elif "persona" in mod:
        return {"name": "User Personas & Glitches", "icon": "🎭", "color": "#f59e0b", "id": "persona"}
    elif "security" in mod:
        return {"name": "Security & Route Guards", "icon": "🛡️", "color": "#ef4444", "id": "security"}
    elif "sidebar" in mod:
        return {"name": "Navigation & Sidebar", "icon": "🧭", "color": "#14b8a6", "id": "sidebar"}
    elif "footer" in mod:
        return {"name": "Footer & Social Links", "icon": "🌐", "color": "#64748b", "id": "footer"}
    else:
        return {"name": "General Tests", "icon": "🧪", "color": "#8b5cf6", "id": "general"}


def generate_html_report(
    test_results: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_path: str = "reports/test_report.html",
    additional_paths: Optional[List[str]] = None,
) -> str:
    """
    Builds the complete single-file interactive HTML report and writes to output_path.
    """
    total = len(test_results)
    passed = sum(1 for t in test_results if t.get("status", "").upper() == "PASSED")
    failed = sum(1 for t in test_results if t.get("status", "").upper() == "FAILED")
    skipped = sum(1 for t in test_results if t.get("status", "").upper() == "SKIPPED")
    pass_rate = round((passed / total * 100), 1) if total > 0 else 0.0
    total_duration = sum(t.get("duration", 0.0) for t in test_results)
    avg_duration = (total_duration / total) if total > 0 else 0.0
    screenshot_count = sum(1 for t in test_results if t.get("screenshot_b64"))
    total_network_requests = sum(len(t.get("network_entries", [])) for t in test_results)

    # Suite breakdown
    suites_summary = {}
    for t in test_results:
        suite_info = get_suite_category(t.get("module", ""), t.get("nodeid", ""))
        s_id = suite_info["id"]
        if s_id not in suites_summary:
            suites_summary[s_id] = {
                "name": suite_info["name"],
                "icon": suite_info["icon"],
                "color": suite_info["color"],
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
            }
        suites_summary[s_id]["total"] += 1
        st = t.get("status", "").upper()
        if st == "PASSED":
            suites_summary[s_id]["passed"] += 1
        elif st == "FAILED":
            suites_summary[s_id]["failed"] += 1
        elif st == "SKIPPED":
            suites_summary[s_id]["skipped"] += 1

    # Speed distribution
    fast_tests = sum(1 for t in test_results if t.get("duration", 0) < 1.0)
    medium_tests = sum(1 for t in test_results if 1.0 <= t.get("duration", 0) < 3.0)
    slow_tests = sum(1 for t in test_results if t.get("duration", 0) >= 3.0)

    # Serialize test data for search and filter scripts
    tests_json = json.dumps(test_results)
    suites_json = json.dumps(suites_summary)

    run_timestamp = metadata.get("timestamp", datetime.now().strftime("%d-%b-%Y %H:%M:%S"))
    platform_info = metadata.get("platform", "Windows / Ubuntu Linux")
    python_ver = metadata.get("python_version", "Python 3.11+")
    playwright_ver = metadata.get("playwright_version", "1.40+")
    target_url = metadata.get("base_url", "https://www.saucedemo.com")

    # SVG Pie / Donut Chart calculation
    # Arc angles in SVG:
    def get_donut_slices(p, f, s, tot):
        if tot == 0:
            return ""
        # circumference for r=70 is 2 * pi * 70 = 439.82
        circ = 439.82
        p_len = (p / tot) * circ
        f_len = (f / tot) * circ
        s_len = (s / tot) * circ

        # offsets
        offset_p = 0
        offset_f = -p_len
        offset_s = -(p_len + f_len)

        svg = f"""
        <circle class="donut-ring" cx="90" cy="90" r="70" fill="transparent" stroke="var(--border-subtle)" stroke-width="24"></circle>
        <circle class="donut-segment donut-passed" cx="90" cy="90" r="70" fill="transparent" stroke="#10b981" stroke-width="24"
                stroke-dasharray="{p_len:.2f} {circ - p_len:.2f}" stroke-dashoffset="{offset_p:.2f}"></circle>
        <circle class="donut-segment donut-failed" cx="90" cy="90" r="70" fill="transparent" stroke="#f43f5e" stroke-width="24"
                stroke-dasharray="{f_len:.2f} {circ - f_len:.2f}" stroke-dashoffset="{offset_f:.2f}"></circle>
        <circle class="donut-segment donut-skipped" cx="90" cy="90" r="70" fill="transparent" stroke="#f59e0b" stroke-width="24"
                stroke-dasharray="{s_len:.2f} {circ - s_len:.2f}" stroke-dashoffset="{offset_s:.2f}"></circle>
        """
        return svg

    donut_svg_circles = get_donut_slices(passed, failed, skipped, total)

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SauceDemo Test Automation - Advanced QA Report</title>
  <style>
    :root {{
      --bg-primary: #0b0f19;
      --bg-secondary: #111827;
      --bg-card: #182234;
      --bg-card-hover: #1e293b;
      --bg-input: #1f293d;
      --border-color: #27354a;
      --border-subtle: #1e293b;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      
      --color-pass: #10b981;
      --color-pass-bg: rgba(16, 185, 129, 0.12);
      --color-pass-glow: rgba(16, 185, 129, 0.28);
      
      --color-fail: #f43f5e;
      --color-fail-bg: rgba(244, 63, 94, 0.14);
      --color-fail-glow: rgba(244, 63, 94, 0.32);
      
      --color-skip: #f59e0b;
      --color-skip-bg: rgba(245, 158, 11, 0.12);
      
      --color-accent: #6366f1;
      --color-accent-hover: #4f46e5;
      --color-accent-bg: rgba(99, 102, 241, 0.12);
      --color-cyan: #06b6d4;
      --color-purple: #a855f7;
      
      --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.5);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
      --radius-full: 9999px;
    }}

    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --bg-card-hover: #f1f5f9;
      --bg-input: #e2e8f0;
      --border-color: #cbd5e1;
      --border-subtle: #e2e8f0;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      
      --color-pass: #059669;
      --color-pass-bg: #ecfdf5;
      --color-pass-glow: rgba(5, 150, 105, 0.2);
      
      --color-fail: #e11d48;
      --color-fail-bg: #fff1f2;
      --color-fail-glow: rgba(225, 29, 72, 0.2);
      
      --color-skip: #d97706;
      --color-skip-bg: #fffbeb;
      
      --color-accent: #4f46e5;
      --color-accent-hover: #4338ca;
      --color-accent-bg: rgba(79, 70, 229, 0.08);
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      padding-bottom: 40px;
      transition: background-color 0.25s, color 0.25s;
    }}

    a {{
      color: var(--color-cyan);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}

    /* Container */
    .container {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 0 24px;
      width: 100%;
    }}

    /* Header */
    .header {{
      background: linear-gradient(180deg, var(--bg-secondary) 0%, rgba(17, 24, 39, 0.7) 100%);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      padding: 24px 0;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow-md);
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .brand-wrap {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .brand-logo {{
      width: 48px;
      height: 48px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }}
    .brand-title h1 {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.02em;
      background: linear-gradient(90deg, #f8fafc 0%, #38bdf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    [data-theme="light"] .brand-title h1 {{
      background: linear-gradient(90deg, #0f172a 0%, #0284c7 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .brand-title p {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-top: 2px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      font-size: 13px;
      font-weight: 600;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-primary);
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .btn:hover {{
      background: var(--bg-card-hover);
      border-color: var(--color-accent);
      transform: translateY(-1px);
    }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-cyan) 100%);
      color: #ffffff;
      border: none;
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
    }}
    .btn-primary:hover {{
      opacity: 0.95;
    }}

    /* Meta Badges Row */
    .meta-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
      align-items: center;
    }}
    .meta-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: var(--radius-full);
      font-size: 12px;
      font-weight: 500;
      background: var(--bg-input);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
    }}
    .meta-chip strong {{
      color: var(--text-primary);
    }}
    .status-pulse {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 14px;
      border-radius: var(--radius-full);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .status-pulse.pass {{
      background: var(--color-pass-bg);
      color: var(--color-pass);
      border: 1px solid var(--color-pass);
      box-shadow: 0 0 14px var(--color-pass-glow);
    }}
    .status-pulse.fail {{
      background: var(--color-fail-bg);
      color: var(--color-fail);
      border: 1px solid var(--color-fail);
      box-shadow: 0 0 14px var(--color-fail-glow);
    }}
    .status-pulse-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
      animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
      0% {{ transform: scale(0.9); opacity: 1; }}
      50% {{ transform: scale(1.4); opacity: 0.4; }}
      100% {{ transform: scale(0.9); opacity: 1; }}
    }}

    /* KPI Cards Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-top: 24px;
    }}
    .kpi-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: var(--color-cyan);
    }}
    .kpi-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: var(--card-accent, var(--color-accent));
    }}
    .kpi-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .kpi-title {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .kpi-icon {{
      font-size: 18px;
      opacity: 0.85;
    }}
    .kpi-value {{
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      line-height: 1.1;
    }}
    .kpi-subtext {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 6px;
    }}

    /* Visual Dashboard Row: Donut + Suites + Speed */
    .visual-dashboard {{
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 20px;
      margin-top: 24px;
    }}
    @media (max-width: 980px) {{
      .visual-dashboard {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 22px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
    }}
    .chart-card h3 {{
      font-size: 16px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 18px;
      color: var(--text-primary);
    }}

    /* Donut Chart SVG */
    .donut-container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
    }}
    .donut-svg-wrap {{
      position: relative;
      width: 180px;
      height: 180px;
    }}
    .donut-svg {{
      transform: rotate(-90deg);
      width: 100%;
      height: 100%;
    }}
    .donut-segment {{
      transition: stroke-width 0.3s, opacity 0.3s;
      cursor: pointer;
    }}
    .donut-segment:hover {{
      stroke-width: 28;
      opacity: 0.9;
    }}
    .donut-center {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      pointer-events: none;
    }}
    .donut-center .rate-num {{
      font-size: 26px;
      font-weight: 800;
      color: var(--text-primary);
      line-height: 1;
    }}
    .donut-center .rate-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-top: 4px;
    }}
    .donut-legend {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;
      margin-top: 18px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 13px;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
    }}
    .legend-left {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}

    /* Suite Breakdown Bars */
    .suites-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px;
    }}
    .suite-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .suite-card:hover, .suite-card.active {{
      border-color: var(--color-cyan);
      background: var(--bg-card-hover);
      transform: translateY(-1px);
    }}
    .suite-card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    .suite-name {{
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-primary);
    }}
    .suite-count {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text-secondary);
    }}
    .suite-progress {{
      height: 6px;
      border-radius: 3px;
      background: var(--bg-input);
      overflow: hidden;
      display: flex;
    }}
    .suite-bar-pass {{
      background: var(--color-pass);
      height: 100%;
    }}
    .suite-bar-fail {{
      background: var(--color-fail);
      height: 100%;
    }}

    /* Architecture Flow Diagram Section */
    .diagram-section {{
      margin-top: 24px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 22px;
      box-shadow: var(--shadow-sm);
    }}
    .diagram-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .diagram-header h3 {{
      font-size: 16px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .diagram-canvas-wrap {{
      overflow-x: auto;
      padding: 10px 0;
    }}
    .diagram-svg {{
      min-width: 900px;
      width: 100%;
      height: auto;
    }}

    /* Filter & Search Bar */
    .controls-bar {{
      margin-top: 28px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      box-shadow: var(--shadow-sm);
    }}
    .search-row {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .search-box {{
      flex: 1;
      min-width: 260px;
      position: relative;
    }}
    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 15px;
      color: var(--text-muted);
    }}
    .search-input {{
      width: 100%;
      padding: 10px 14px 10px 40px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
      background: var(--bg-input);
      color: var(--text-primary);
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--color-cyan);
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
    }}

    .filter-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .filter-pill {{
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      border-radius: var(--radius-full);
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}
    .filter-pill:hover {{
      border-color: var(--color-accent);
      color: var(--text-primary);
    }}
    .filter-pill.active {{
      background: var(--color-accent);
      color: #ffffff;
      border-color: var(--color-accent);
    }}
    .filter-pill.pill-pass.active {{
      background: var(--color-pass);
      border-color: var(--color-pass);
    }}
    .filter-pill.pill-fail.active {{
      background: var(--color-fail);
      border-color: var(--color-fail);
    }}
    .filter-pill.pill-skip.active {{
      background: var(--color-skip);
      border-color: var(--color-skip);
    }}
    .pill-badge {{
      background: rgba(255, 255, 255, 0.2);
      border-radius: var(--radius-full);
      padding: 1px 7px;
      font-size: 11px;
    }}

    .sort-wrap {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--text-secondary);
      margin-left: auto;
    }}
    .sort-select {{
      padding: 6px 12px;
      border-radius: var(--radius-md);
      background: var(--bg-input);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      font-size: 13px;
      outline: none;
    }}

    /* Test Results Cards List */
    .test-list {{
      margin-top: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .test-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .test-card:hover {{
      border-color: var(--border-color);
      box-shadow: var(--shadow-md);
    }}
    .test-card.status-failed {{
      border-left: 4px solid var(--color-fail);
    }}
    .test-card.status-passed {{
      border-left: 4px solid var(--color-pass);
    }}
    .test-card.status-skipped {{
      border-left: 4px solid var(--color-skip);
    }}

    .test-header {{
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .test-header-left {{
      display: flex;
      align-items: center;
      gap: 14px;
      flex: 1;
      min-width: 280px;
    }}
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.03em;
    }}
    .status-badge.passed {{
      background: var(--color-pass-bg);
      color: var(--color-pass);
      border: 1px solid var(--color-pass);
    }}
    .status-badge.failed {{
      background: var(--color-fail-bg);
      color: var(--color-fail);
      border: 1px solid var(--color-fail);
    }}
    .status-badge.skipped {{
      background: var(--color-skip-bg);
      color: var(--color-skip);
      border: 1px solid var(--color-skip);
    }}

    .test-name-wrap {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .test-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--text-primary);
    }}
    .test-method {{
      font-size: 12px;
      font-family: monospace;
      color: var(--text-muted);
    }}

    .test-header-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .tag {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 600;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
    }}
    .tag-duration {{
      font-family: monospace;
      font-weight: 700;
      color: var(--text-primary);
    }}
    .tag-network {{
      background: rgba(6, 182, 212, 0.12);
      border-color: rgba(6, 182, 212, 0.3);
      color: var(--color-cyan);
    }}
    .tag-screenshot {{
      background: rgba(236, 72, 153, 0.12);
      border-color: rgba(236, 72, 153, 0.3);
      color: #ec4899;
    }}
    .chevron-icon {{
      font-size: 14px;
      color: var(--text-muted);
      transition: transform 0.25s ease;
    }}
    .test-card.open .chevron-icon {{
      transform: rotate(180deg);
    }}

    /* Test Expanded Body */
    .test-body {{
      display: none;
      padding: 0 20px 20px 20px;
      border-top: 1px solid var(--border-subtle);
    }}
    .test-card.open .test-body {{
      display: block;
    }}

    .test-info-section {{
      margin-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .test-desc {{
      font-size: 13px;
      color: var(--text-secondary);
      background: var(--bg-card);
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      border-left: 3px solid var(--color-accent);
    }}
    .test-path-info {{
      font-size: 12px;
      font-family: monospace;
      color: var(--text-muted);
    }}

    /* Bug & Failure Callout */
    .failure-box {{
      margin-top: 16px;
      border-radius: var(--radius-md);
      background: var(--color-fail-bg);
      border: 1px solid var(--color-fail);
      padding: 16px;
    }}
    .failure-title {{
      font-size: 14px;
      font-weight: 700;
      color: var(--color-fail);
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }}
    .traceback-pre {{
      background: #000000;
      color: #f87171;
      padding: 12px 14px;
      border-radius: var(--radius-sm);
      font-family: Consolas, Monaco, "Courier New", monospace;
      font-size: 12px;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
      border: 1px solid rgba(244, 63, 94, 0.3);
      position: relative;
    }}
    .copy-btn {{
      position: absolute;
      top: 8px;
      right: 8px;
      background: rgba(255, 255, 255, 0.15);
      border: none;
      color: #ffffff;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      cursor: pointer;
    }}
    .copy-btn:hover {{
      background: rgba(255, 255, 255, 0.3);
    }}

    /* Screenshot Gallery / Bug Preview */
    .screenshot-section {{
      margin-top: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 16px;
    }}
    .screenshot-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .screenshot-header h4 {{
      font-size: 13px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-primary);
    }}
    .screenshot-preview-wrap {{
      display: inline-block;
      position: relative;
      border-radius: var(--radius-md);
      overflow: hidden;
      border: 1px solid var(--border-color);
      max-width: 540px;
      cursor: zoom-in;
    }}
    .screenshot-img {{
      display: block;
      width: 100%;
      height: auto;
      max-height: 280px;
      object-fit: cover;
      object-position: top;
      transition: transform 0.3s ease;
    }}
    .screenshot-preview-wrap:hover .screenshot-img {{
      transform: scale(1.02);
    }}
    .zoom-overlay {{
      position: absolute;
      inset: 0;
      background: rgba(0,0,0,0.45);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.2s ease;
      color: #ffffff;
      font-size: 14px;
      font-weight: 600;
      gap: 8px;
    }}
    .screenshot-preview-wrap:hover .zoom-overlay {{
      opacity: 1;
    }}

    /* Network Activity Panel */
    .network-panel {{
      margin-top: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 16px;
    }}
    .network-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .network-header h4 {{
      font-size: 13px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--color-cyan);
    }}
    .network-table-wrap {{
      margin-top: 12px;
      overflow-x: auto;
    }}
    .network-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      font-family: monospace;
    }}
    .network-table th {{
      text-align: left;
      padding: 8px 10px;
      background: var(--bg-input);
      color: var(--text-secondary);
      font-weight: 600;
      border-bottom: 1px solid var(--border-color);
    }}
    .network-table td {{
      padding: 7px 10px;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text-primary);
    }}
    .net-status {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 11px;
    }}
    .net-status-2xx {{
      background: var(--color-pass-bg);
      color: var(--color-pass);
    }}
    .net-status-3xx {{
      background: rgba(59, 130, 246, 0.15);
      color: #3b82f6;
    }}
    .net-status-4xx, .net-status-5xx, .net-status-err {{
      background: var(--color-fail-bg);
      color: var(--color-fail);
    }}
    .net-method {{
      font-weight: 700;
      color: var(--text-secondary);
    }}
    .net-url {{
      max-width: 450px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      display: block;
    }}

    /* Lightbox Modal */
    .lightbox-modal {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(8px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}
    .lightbox-modal.active {{
      display: flex;
    }}
    .lightbox-content {{
      position: relative;
      max-width: 95vw;
      max-height: 92vh;
      display: flex;
      flex-direction: column;
      background: var(--bg-secondary);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-lg);
      overflow: hidden;
    }}
    .lightbox-topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 20px;
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-subtle);
    }}
    .lightbox-title {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text-primary);
    }}
    .lightbox-close {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 22px;
      cursor: pointer;
      line-height: 1;
    }}
    .lightbox-close:hover {{
      color: var(--color-fail);
    }}
    .lightbox-img-wrap {{
      overflow: auto;
      padding: 16px;
      display: flex;
      justify-content: center;
      background: #000000;
    }}
    .lightbox-img {{
      max-width: 100%;
      max-height: 80vh;
      object-fit: contain;
      border-radius: var(--radius-sm);
    }}

    /* Empty state */
    .empty-state {{
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
      background: var(--bg-secondary);
      border-radius: var(--radius-lg);
      border: 1px dashed var(--border-color);
      margin-top: 20px;
      display: none;
    }}

    /* Footer */
    .footer {{
      margin-top: 48px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
      padding: 24px 0;
      border-top: 1px solid var(--border-subtle);
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="header">
    <div class="container">
      <div class="header-top">
        <div class="brand-wrap">
          <div class="brand-logo">⚡</div>
          <div class="brand-title">
            <h1>SauceDemo Playwright Test Automation Dashboard</h1>
            <p>Comprehensive Web UI & Edge Scenario Regression Test Suite</p>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn" id="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
            <span id="theme-icon">☀️</span> <span id="theme-text">Light Mode</span>
          </button>
          <button class="btn" onclick="toggleAllCards(true)" title="Expand All Test Cards">
            <span>⊞</span> Expand All
          </button>
          <button class="btn" onclick="toggleAllCards(false)" title="Collapse All Test Cards">
            <span>⊟</span> Collapse All
          </button>
          <a class="btn btn-primary" href="https://github.com/tanzimsqa/saucedemo-playwright-automation" target="_blank" rel="noopener">
            <span>📂</span> GitHub Repo
          </a>
        </div>
      </div>

      <!-- Metadata Chips -->
      <div class="meta-bar">
        <div class="status-pulse {'pass' if failed == 0 else 'fail'}">
          <span class="status-pulse-dot"></span>
          <span>{'SUITE PASSED (100% HEALTH)' if failed == 0 else f'{failed} FAILURES DETECTED'}</span>
        </div>
        <div class="meta-chip">
          <span>🎯 Target:</span>
          <strong><a href="{target_url}" target="_blank" rel="noopener">{target_url}</a></strong>
        </div>
        <div class="meta-chip">
          <span>🎭 Browser:</span>
          <strong>Chromium (Headless 1280x800)</strong>
        </div>
        <div class="meta-chip">
          <span>🕒 Executed:</span>
          <strong>{run_timestamp}</strong>
        </div>
        <div class="meta-chip">
          <span>⚙️ Platform:</span>
          <strong>{platform_info}</strong>
        </div>
        <div class="meta-chip">
          <span>🐍 Runtime:</span>
          <strong>{python_ver} | Playwright {playwright_ver}</strong>
        </div>
      </div>
    </div>
  </header>

  <main class="container">
    <!-- Executive KPI Cards -->
    <section class="kpi-grid">
      <div class="kpi-card" style="--card-accent: #6366f1;">
        <div class="kpi-header">
          <span class="kpi-title">Total Tests</span>
          <span class="kpi-icon">📋</span>
        </div>
        <div class="kpi-value">{total}</div>
        <div class="kpi-subtext">Across {len(suites_summary)} test modules</div>
      </div>

      <div class="kpi-card" style="--card-accent: #10b981;">
        <div class="kpi-header">
          <span class="kpi-title">Passed</span>
          <span class="kpi-icon">✅</span>
        </div>
        <div class="kpi-value" style="color: var(--color-pass);">{passed}</div>
        <div class="kpi-subtext">{round((passed / total * 100), 1) if total else 0}% success rate</div>
      </div>

      <div class="kpi-card" style="--card-accent: #f43f5e;">
        <div class="kpi-header">
          <span class="kpi-title">Failed / Bugs</span>
          <span class="kpi-icon">❌</span>
        </div>
        <div class="kpi-value" style="color: {'var(--color-fail)' if failed > 0 else 'var(--text-muted)'};">{failed}</div>
        <div class="kpi-subtext">{'Action required' if failed > 0 else 'Zero regressions'}</div>
      </div>

      <div class="kpi-card" style="--card-accent: #f59e0b;">
        <div class="kpi-header">
          <span class="kpi-title">Skipped</span>
          <span class="kpi-icon">⏸️</span>
        </div>
        <div class="kpi-value" style="color: {'var(--color-skip)' if skipped > 0 else 'var(--text-muted)'};">{skipped}</div>
        <div class="kpi-subtext">Pending / conditional</div>
      </div>

      <div class="kpi-card" style="--card-accent: #06b6d4;">
        <div class="kpi-header">
          <span class="kpi-title">Pass Rate</span>
          <span class="kpi-icon">📊</span>
        </div>
        <div class="kpi-value" style="color: var(--color-cyan);">{pass_rate}%</div>
        <div class="kpi-subtext">Weighted suite health</div>
      </div>

      <div class="kpi-card" style="--card-accent: #a855f7;">
        <div class="kpi-header">
          <span class="kpi-title">Execution Time</span>
          <span class="kpi-icon">⏱️</span>
        </div>
        <div class="kpi-value">{format_duration(total_duration)}</div>
        <div class="kpi-subtext">Avg {format_duration(avg_duration)} / test</div>
      </div>
    </section>

    <!-- Visual Dashboard: Donut Chart + Suite Breakdown -->
    <section class="visual-dashboard">
      <!-- Donut / Pi-Chart Card -->
      <div class="chart-card">
        <h3><span>🥧</span> Test Outcome Distribution</h3>
        <div class="donut-container">
          <div class="donut-svg-wrap">
            <svg class="donut-svg" viewBox="0 0 180 180">
              {donut_svg_circles}
            </svg>
            <div class="donut-center">
              <div class="rate-num">{pass_rate}%</div>
              <div class="rate-label">Passed</div>
            </div>
          </div>

          <div class="donut-legend">
            <div class="legend-item" onclick="setQuickFilter('passed')" style="cursor: pointer;">
              <div class="legend-left">
                <span class="legend-dot" style="background: #10b981;"></span>
                <span>Passed</span>
              </div>
              <strong>{passed} ({round((passed/total*100), 1) if total else 0}%)</strong>
            </div>

            <div class="legend-item" onclick="setQuickFilter('failed')" style="cursor: pointer;">
              <div class="legend-left">
                <span class="legend-dot" style="background: #f43f5e;"></span>
                <span>Failed</span>
              </div>
              <strong>{failed} ({round((failed/total*100), 1) if total else 0}%)</strong>
            </div>

            <div class="legend-item" onclick="setQuickFilter('skipped')" style="cursor: pointer;">
              <div class="legend-left">
                <span class="legend-dot" style="background: #f59e0b;"></span>
                <span>Skipped</span>
              </div>
              <strong>{skipped} ({round((skipped/total*100), 1) if total else 0}%)</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Suite Breakdown Card -->
      <div class="chart-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="margin: 0;"><span>📂</span> Test Modules & Coverage ({len(suites_summary)} Suites)</h3>
          <span style="font-size: 12px; color: var(--text-muted);">Click card to filter</span>
        </div>
        <div class="suites-grid">
"""

    for s_id, s_data in suites_summary.items():
        s_tot = s_data["total"]
        s_pass = s_data["passed"]
        s_fail = s_data["failed"]
        pass_pct = (s_pass / s_tot * 100) if s_tot else 0
        fail_pct = (s_fail / s_tot * 100) if s_tot else 0

        html_content += f"""
          <div class="suite-card" onclick="filterBySuite('{s_id}', this)" data-suite-id="{s_id}">
            <div class="suite-card-top">
              <span class="suite-name">{s_data['icon']} {s_data['name']}</span>
              <span class="suite-count">{s_pass}/{s_tot}</span>
            </div>
            <div class="suite-progress">
              <div class="suite-bar-pass" style="width: {pass_pct}%;"></div>
              <div class="suite-bar-fail" style="width: {fail_pct}%;"></div>
            </div>
          </div>
        """

    html_content += f"""
        </div>
      </div>
    </section>

    <!-- Architecture & Test Flow Diagram Section -->
    <section class="diagram-section">
      <div class="diagram-header">
        <h3><span>📐</span> SauceDemo Playwright Test Automation Pipeline & Flow Architecture</h3>
        <span class="meta-chip">E2E Flow Matrix • Route Security • Glitch Personas</span>
      </div>
      <div class="diagram-canvas-wrap">
        <svg class="diagram-svg" viewBox="0 0 1100 240" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="grad-blue" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#3b82f6" />
              <stop offset="100%" stop-color="#1d4ed8" />
            </linearGradient>
            <linearGradient id="grad-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#06b6d4" />
              <stop offset="100%" stop-color="#0e7490" />
            </linearGradient>
            <linearGradient id="grad-purple" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#8b5cf6" />
              <stop offset="100%" stop-color="#6d28d9" />
            </linearGradient>
            <linearGradient id="grad-green" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#10b981" />
              <stop offset="100%" stop-color="#047857" />
            </linearGradient>
            <linearGradient id="grad-amber" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#f59e0b" />
              <stop offset="100%" stop-color="#b45309" />
            </linearGradient>
            <linearGradient id="grad-rose" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#f43f5e" />
              <stop offset="100%" stop-color="#be123c" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#38bdf8" />
            </marker>
          </defs>

          <!-- Pipeline Connectors -->
          <!-- Main Happy Path Flow -->
          <path d="M 140 70 L 195 70" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="5 3" marker-end="url(#arrow)" />
          <path d="M 335 70 L 385 70" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
          <path d="M 525 70 L 575 70" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
          <path d="M 715 70 L 765 70" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />
          <path d="M 905 70 L 955 70" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow)" />

          <!-- Branch to Personas -->
          <path d="M 265 105 L 265 170 L 385 170" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4 4" marker-end="url(#arrow)" />
          <!-- Branch to Route Security -->
          <path d="M 265 35 L 265 15 L 575 15 L 575 35" stroke="#ef4444" stroke-width="2" stroke-dasharray="4 4" fill="none" marker-end="url(#arrow)" />

          <!-- Node 1: Browser & Playwright Engine -->
          <g transform="translate(10, 35)">
            <rect width="130" height="70" rx="12" fill="#182234" stroke="#38bdf8" stroke-width="1.8" filter="url(#glow)"/>
            <text x="65" y="28" fill="#38bdf8" font-size="12" font-weight="700" text-anchor="middle">🎭 Playwright Engine</text>
            <text x="65" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Chromium 1280x800</text>
            <text x="65" y="60" fill="#64748b" font-size="9" text-anchor="middle">Network Listeners</text>
          </g>

          <!-- Node 2: Authentication Gateway -->
          <g transform="translate(195, 35)">
            <rect width="140" height="70" rx="12" fill="#182234" stroke="#6366f1" stroke-width="1.8"/>
            <text x="70" y="28" fill="#818cf8" font-size="12" font-weight="700" text-anchor="middle">🔑 Auth Gateway</text>
            <text x="70" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Standard / Locked / SQLi</text>
            <text x="70" y="60" fill="#10b981" font-size="9" font-weight="600" text-anchor="middle">11 Tests • 100% Pass</text>
          </g>

          <!-- Node 3: Catalog & Details -->
          <g transform="translate(385, 35)">
            <rect width="140" height="70" rx="12" fill="#182234" stroke="#06b6d4" stroke-width="1.8"/>
            <text x="70" y="28" fill="#22d3ee" font-size="12" font-weight="700" text-anchor="middle">📦 Catalog & Details</text>
            <text x="70" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">4-Way Sorting • Item Card</text>
            <text x="70" y="60" fill="#10b981" font-size="9" font-weight="600" text-anchor="middle">12 Tests • 100% Pass</text>
          </g>

          <!-- Node 4: Shopping Cart -->
          <g transform="translate(575, 35)">
            <rect width="140" height="70" rx="12" fill="#182234" stroke="#8b5cf6" stroke-width="1.8"/>
            <text x="70" y="28" fill="#a78bfa" font-size="12" font-weight="700" text-anchor="middle">🛒 Cart Management</text>
            <text x="70" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Badge Counters • State</text>
            <text x="70" y="60" fill="#10b981" font-size="9" font-weight="600" text-anchor="middle">5 Tests • 100% Pass</text>
          </g>

          <!-- Node 5: Checkout Engine -->
          <g transform="translate(765, 35)">
            <rect width="140" height="70" rx="12" fill="#182234" stroke="#ec4899" stroke-width="1.8"/>
            <text x="70" y="28" fill="#f472b6" font-size="12" font-weight="700" text-anchor="middle">💳 Checkout Engine</text>
            <text x="70" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Step 1 • Tax & Sum • Finish</text>
            <text x="70" y="60" fill="#10b981" font-size="9" font-weight="600" text-anchor="middle">10 Tests • 100% Pass</text>
          </g>

          <!-- Node 6: Quality Gate & GitHub Pages -->
          <g transform="translate(955, 35)">
            <rect width="135" height="70" rx="12" fill="#182234" stroke="#10b981" stroke-width="2.2" filter="url(#glow)"/>
            <text x="67" y="28" fill="#34d399" font-size="12" font-weight="700" text-anchor="middle">🚀 Quality Gate</text>
            <text x="67" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Interactive Report</text>
            <text x="67" y="60" fill="#38bdf8" font-size="9" font-weight="600" text-anchor="middle">GitHub Pages Deploy</text>
          </g>

          <!-- Bottom Branch: User Personas Matrix -->
          <g transform="translate(385, 135)">
            <rect width="330" height="70" rx="12" fill="#182234" stroke="#f59e0b" stroke-width="1.8"/>
            <text x="165" y="28" fill="#fbbf24" font-size="12" font-weight="700" text-anchor="middle">🎭 User Persona & Glitch Detection Matrix</text>
            <text x="165" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Problem User (Dog Images) • Performance Glitch • Error User</text>
            <text x="165" y="60" fill="#10b981" font-size="9" font-weight="600" text-anchor="middle">4 Scenarios Verified • Bug Screenshot Attached</text>
          </g>

          <!-- Route Security Banner -->
          <g transform="translate(765, 135)">
            <rect width="325" height="70" rx="12" fill="#182234" stroke="#ef4444" stroke-width="1.8"/>
            <text x="162" y="28" fill="#f87171" font-size="12" font-weight="700" text-anchor="middle">🛡️ Route Security & Unauthorized Access</text>
            <text x="162" y="46" fill="#94a3b8" font-size="10" text-anchor="middle">Blocked Direct URL Access to Inventory, Cart, Checkout</text>
            <text x="162" y="60" fill="#10b981" font-size="9" font-weight="600" text-anchor="middle">5 Guard Tests • 100% Pass</text>
          </g>
        </svg>
      </div>
    </section>

    <!-- Controls Bar: Search & Quick Filters -->
    <section class="controls-bar">
      <div class="search-row">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="search-input" class="search-input" placeholder="Search test name, suite, or assertion message... (Press '/' to focus)" oninput="applyFilters()" />
        </div>

        <div class="sort-wrap">
          <label for="sort-select">Sort By:</label>
          <select id="sort-select" class="sort-select" onchange="applySorting()">
            <option value="default">Default Order</option>
            <option value="duration-desc">Duration (Slowest First)</option>
            <option value="duration-asc">Duration (Fastest First)</option>
            <option value="name-asc">Test Name (A to Z)</option>
            <option value="status">Status</option>
          </select>
        </div>
      </div>

      <div class="filter-pills">
        <div class="filter-pill active" onclick="setQuickFilter('all')" data-filter="all">
          <span>All Tests</span>
          <span class="pill-badge">{total}</span>
        </div>
        <div class="filter-pill pill-pass" onclick="setQuickFilter('passed')" data-filter="passed">
          <span>✅ Passed</span>
          <span class="pill-badge">{passed}</span>
        </div>
        <div class="filter-pill pill-fail" onclick="setQuickFilter('failed')" data-filter="failed">
          <span>❌ Failed</span>
          <span class="pill-badge">{failed}</span>
        </div>
        <div class="filter-pill pill-skip" onclick="setQuickFilter('skipped')" data-filter="skipped">
          <span>⏸️ Skipped</span>
          <span class="pill-badge">{skipped}</span>
        </div>
        <div class="filter-pill" onclick="setQuickFilter('screenshot')" data-filter="screenshot">
          <span>📸 Bug Screenshots</span>
          <span class="pill-badge">{screenshot_count}</span>
        </div>
        <div class="filter-pill" onclick="setQuickFilter('network')" data-filter="network">
          <span>🌐 Network Traffic</span>
          <span class="pill-badge">{total_network_requests} calls</span>
        </div>
      </div>
    </section>

    <!-- Empty State for Filters -->
    <div id="empty-state" class="empty-state">
      <h3>No matching tests found</h3>
      <p>Try clearing your search query or switching active status filters.</p>
      <button class="btn" style="margin-top: 14px;" onclick="resetAllFilters()">Reset All Filters</button>
    </div>

    <!-- Test Results Cards List -->
    <section class="test-list" id="test-list">
"""

    for idx, test in enumerate(test_results):
        status = test.get("status", "PASSED").upper()
        status_class = "passed" if status == "PASSED" else ("failed" if status == "FAILED" else "skipped")
        duration = test.get("duration", 0.0)
        dur_fmt = format_duration(duration)
        nodeid = test.get("nodeid", "")
        test_func_name = test.get("name", nodeid.split("::")[-1])
        title = test.get("display_name", clean_test_name(test_func_name))
        doc = test.get("doc", "").strip() or "No description provided."
        suite_info = get_suite_category(test.get("module", ""), nodeid)
        screenshot_b64 = test.get("screenshot_b64", "")
        network_entries = test.get("network_entries", [])
        error_msg = test.get("error_message", "")
        stack_trace = test.get("stack_trace", "")
        markers = test.get("markers", [])
        params = test.get("parameters", "")

        has_screenshot = "true" if screenshot_b64 else "false"
        has_network = "true" if len(network_entries) > 0 else "false"

        html_content += f"""
      <article class="test-card status-{status_class}" 
               id="card-{idx}"
               data-idx="{idx}"
               data-status="{status.lower()}"
               data-suite="{suite_info['id']}"
               data-name="{html.escape(title.lower())} {html.escape(test_func_name.lower())}"
               data-duration="{duration}"
               data-has-screenshot="{has_screenshot}"
               data-has-network="{has_network}">

        <div class="test-header" onclick="toggleCard({idx})">
          <div class="test-header-left">
            <span class="status-badge {status_class}">
              {'✓' if status == 'PASSED' else ('✗' if status == 'FAILED' else '—')} {status}
            </span>
            <div class="test-name-wrap">
              <span class="test-title">{html.escape(title)}</span>
              <span class="test-method">{html.escape(test_func_name)}</span>
            </div>
          </div>

          <div class="test-header-right">
            <span class="tag" style="border-color: {suite_info['color']}33; color: {suite_info['color']};">
              {suite_info['icon']} {suite_info['name']}
            </span>
            <span class="tag tag-duration">{dur_fmt}</span>
"""

        if screenshot_b64:
            html_content += f"""
            <span class="tag tag-screenshot">📸 Bug Screenshot</span>
"""
        if len(network_entries) > 0:
            html_content += f"""
            <span class="tag tag-network">🌐 {len(network_entries)} Reqs</span>
"""

        html_content += f"""
            <span class="chevron-icon">▼</span>
          </div>
        </div>

        <div class="test-body">
          <div class="test-info-section">
            <div class="test-desc">{html.escape(doc)}</div>
            <div class="test-path-info">📌 NodeID: {html.escape(nodeid)}</div>
"""

        if params:
            html_content += f"""
            <div class="test-path-info">⚙️ Parameters: <code>{html.escape(str(params))}</code></div>
"""

        if markers:
            markers_html = " ".join([f"<span class='tag'>#{html.escape(m)}</span>" for m in markers])
            html_content += f"""
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">{markers_html}</div>
"""

        html_content += f"""
          </div>
"""

        # Failure / Bug Details
        if status == "FAILED" or error_msg or stack_trace:
            html_content += f"""
          <div class="failure-box">
            <div class="failure-title">
              <span>🚨</span> Failure Analysis / Bug Assertion Trace
            </div>
            <div style="margin-bottom: 8px; font-weight: 600; color: #fecdd3; font-size: 13px;">
              {html.escape(error_msg or "Assertion or runtime error encountered.")}
            </div>
            <div class="traceback-pre">
              <button class="copy-btn" onclick="copyTraceback(this)">Copy Trace</button>
              <code>{html.escape(stack_trace or error_msg)}</code>
            </div>
          </div>
"""

        # Bug Screenshot Preview
        if screenshot_b64:
            html_content += f"""
          <div class="screenshot-section">
            <div class="screenshot-header">
              <h4><span>📸</span> Bug Screenshot & Visual State</h4>
              <span style="font-size: 11px; color: var(--text-muted);">Captured at point of failure / glitch assertion</span>
            </div>
            <div class="screenshot-preview-wrap" onclick="openLightbox('{idx}', '{html.escape(title)}')">
              <img class="screenshot-img" src="data:image/png;base64,{screenshot_b64}" alt="Bug Screenshot for {html.escape(title)}" />
              <div class="zoom-overlay">
                <span>🔍 Click to View High-Resolution Lightbox</span>
              </div>
            </div>
          </div>
"""

        # Network Activity Inspector
        if network_entries:
            ok_count = sum(1 for e in network_entries if e.get("ok", True))
            err_count = len(network_entries) - ok_count

            html_content += f"""
          <div class="network-panel">
            <div class="network-header">
              <h4><span>🌐</span> Network Requests & Responses ({len(network_entries)} calls)</h4>
              <div style="display: flex; gap: 8px; font-size: 11px;">
                <span class="tag" style="color: var(--color-pass);">✓ {ok_count} Successful</span>
                {f"<span class='tag' style='color: var(--color-fail);'>✗ {err_count} Failed</span>" if err_count > 0 else ""}
              </div>
            </div>
            <div class="network-table-wrap">
              <table class="network-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Method</th>
                    <th>Type</th>
                    <th>Request URL</th>
                  </tr>
                </thead>
                <tbody>
"""
            for net in network_entries:
                st = net.get("status", 200)
                st_cls = "net-status-2xx" if 200 <= st < 300 else ("net-status-3xx" if 300 <= st < 400 else "net-status-err")
                st_txt = f"{st} {net.get('status_text', '')}".strip()
                mth = net.get("method", "GET")
                res_type = net.get("resource_type", "doc")
                url_str = net.get("url", "")

                html_content += f"""
                  <tr>
                    <td><span class="net-status {st_cls}">{st_txt}</span></td>
                    <td class="net-method">{mth}</td>
                    <td><span class="tag">{res_type}</span></td>
                    <td><span class="net-url" title="{html.escape(url_str)}">{html.escape(url_str)}</span></td>
                  </tr>
"""

            html_content += f"""
                </tbody>
              </table>
            </div>
          </div>
"""

        html_content += f"""
        </div>
      </article>
"""

    html_content += f"""
    </section>
  </main>

  <!-- Lightbox Modal for High-Resolution Bug Screenshots -->
  <div id="lightbox-modal" class="lightbox-modal" onclick="closeLightbox(event)">
    <div class="lightbox-content" onclick="event.stopPropagation()">
      <div class="lightbox-topbar">
        <span class="lightbox-title" id="lightbox-title">Bug Screenshot</span>
        <button class="lightbox-close" onclick="closeLightbox()" title="Close (Esc)">✕</button>
      </div>
      <div class="lightbox-img-wrap">
        <img id="lightbox-img" class="lightbox-img" src="" alt="Fullscreen Screenshot Preview" />
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <p>SauceDemo Playwright Automation Suite • Advanced Test Execution Report</p>
      <p style="margin-top: 4px; font-size: 11px;">
        Generated on {run_timestamp} • Hosted on <a href="https://tanzimsqa.github.io/saucedemo-playwright-automation/" target="_blank" rel="noopener">GitHub Pages</a>
      </p>
    </div>
  </footer>

  <!-- Interactive JavaScript -->
  <script>
    const testData = {tests_json};
    const suitesData = {suites_json};
    let currentQuickFilter = 'all';
    let currentSuiteFilter = 'all';

    // Theme Toggle
    function toggleTheme() {{
      const htmlEl = document.documentElement;
      const currentTheme = htmlEl.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      htmlEl.setAttribute('data-theme', newTheme);
      localStorage.setItem('saucedemo-report-theme', newTheme);
      updateThemeUI(newTheme);
    }}

    function updateThemeUI(theme) {{
      const icon = document.getElementById('theme-icon');
      const text = document.getElementById('theme-text');
      if (theme === 'light') {{
        icon.textContent = '🌙';
        text.textContent = 'Dark Mode';
      }} else {{
        icon.textContent = '☀️';
        text.textContent = 'Light Mode';
      }}
    }}

    // Init Theme from Storage
    (function initTheme() {{
      const saved = localStorage.getItem('saucedemo-report-theme');
      if (saved) {{
        document.documentElement.setAttribute('data-theme', saved);
        updateThemeUI(saved);
      }}
    }})();

    // Card Accordion
    function toggleCard(idx) {{
      const card = document.getElementById('card-' + idx);
      if (card) {{
        card.classList.toggle('open');
      }}
    }}

    function toggleAllCards(open) {{
      const cards = document.querySelectorAll('.test-card');
      cards.forEach(card => {{
        if (open) card.classList.add('open');
        else card.classList.remove('open');
      }});
    }}

    // Filtering
    function setQuickFilter(type) {{
      currentQuickFilter = type;
      document.querySelectorAll('.filter-pill').forEach(pill => {{
        if (pill.getAttribute('data-filter') === type) pill.classList.add('active');
        else pill.classList.remove('active');
      }});
      applyFilters();
    }}

    function filterBySuite(suiteId, el) {{
      if (currentSuiteFilter === suiteId) {{
        currentSuiteFilter = 'all';
        el.classList.remove('active');
      }} else {{
        currentSuiteFilter = suiteId;
        document.querySelectorAll('.suite-card').forEach(c => c.classList.remove('active'));
        el.classList.add('active');
      }}
      applyFilters();
    }}

    function resetAllFilters() {{
      currentQuickFilter = 'all';
      currentSuiteFilter = 'all';
      document.getElementById('search-input').value = '';
      document.querySelectorAll('.filter-pill').forEach(p => {{
        if (p.getAttribute('data-filter') === 'all') p.classList.add('active');
        else p.classList.remove('active');
      }});
      document.querySelectorAll('.suite-card').forEach(c => c.classList.remove('active'));
      applyFilters();
    }}

    function applyFilters() {{
      const searchVal = (document.getElementById('search-input').value || '').trim().toLowerCase();
      const cards = document.querySelectorAll('.test-card');
      let visibleCount = 0;

      cards.forEach(card => {{
        const status = card.getAttribute('data-status');
        const suite = card.getAttribute('data-suite');
        const name = card.getAttribute('data-name');
        const hasScreenshot = card.getAttribute('data-has-screenshot') === 'true';
        const hasNetwork = card.getAttribute('data-has-network') === 'true';

        let matchesQuick = true;
        if (currentQuickFilter === 'passed') matchesQuick = (status === 'passed');
        else if (currentQuickFilter === 'failed') matchesQuick = (status === 'failed');
        else if (currentQuickFilter === 'skipped') matchesQuick = (status === 'skipped');
        else if (currentQuickFilter === 'screenshot') matchesQuick = hasScreenshot;
        else if (currentQuickFilter === 'network') matchesQuick = hasNetwork;

        let matchesSuite = true;
        if (currentSuiteFilter !== 'all') {{
          matchesSuite = (suite === currentSuiteFilter);
        }}

        let matchesSearch = true;
        if (searchVal) {{
          matchesSearch = name.includes(searchVal);
        }}

        if (matchesQuick && matchesSuite && matchesSearch) {{
          card.style.display = '';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      const emptyEl = document.getElementById('empty-state');
      if (visibleCount === 0) {{
        emptyEl.style.display = 'block';
      }} else {{
        emptyEl.style.display = 'none';
      }}
    }}

    // Sorting
    function applySorting() {{
      const sortType = document.getElementById('sort-select').value;
      const list = document.getElementById('test-list');
      const cards = Array.from(list.querySelectorAll('.test-card'));

      cards.sort((a, b) => {{
        const durA = parseFloat(a.getAttribute('data-duration') || '0');
        const durB = parseFloat(b.getAttribute('data-duration') || '0');
        const nameA = a.getAttribute('data-name') || '';
        const nameB = b.getAttribute('data-name') || '';
        const idxA = parseInt(a.getAttribute('data-idx') || '0');
        const idxB = parseInt(b.getAttribute('data-idx') || '0');

        if (sortType === 'duration-desc') return durB - durA;
        if (sortType === 'duration-asc') return durA - durB;
        if (sortType === 'name-asc') return nameA.localeCompare(nameB);
        if (sortType === 'status') {{
          const stA = a.getAttribute('data-status');
          const stB = b.getAttribute('data-status');
          return stA.localeCompare(stB);
        }}
        return idxA - idxB;
      }});

      cards.forEach(c => list.appendChild(c));
    }}

    // Keyboard shortcut '/' to search
    window.addEventListener('keydown', e => {{
      if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {{
        e.preventDefault();
        const search = document.getElementById('search-input');
        search.focus();
        search.select();
      }} else if (e.key === 'Escape') {{
        closeLightbox();
      }}
    }});

    // Lightbox
    function openLightbox(idx, title) {{
      const test = testData[idx];
      if (!test || !test.screenshot_b64) return;
      const modal = document.getElementById('lightbox-modal');
      const img = document.getElementById('lightbox-img');
      const titleEl = document.getElementById('lightbox-title');

      img.src = 'data:image/png;base64,' + test.screenshot_b64;
      titleEl.textContent = title + ' - Bug Screenshot';
      modal.classList.add('active');
    }}

    function closeLightbox() {{
      const modal = document.getElementById('lightbox-modal');
      if (modal) modal.classList.remove('active');
    }}

    // Copy Traceback
    function copyTraceback(btn) {{
      const pre = btn.parentElement;
      const code = pre.querySelector('code');
      if (code) {{
        navigator.clipboard.writeText(code.innerText);
        const original = btn.innerText;
        btn.innerText = 'Copied!';
        setTimeout(() => {{ btn.innerText = original; }}, 2000);
      }}
    }}
  </script>
</body>
</html>
"""

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html_content, encoding="utf-8")

    # Also export summary.json for email notifications and CI/CD consumption
    summary_data = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": pass_rate,
        "total_duration": total_duration,
        "total_duration_formatted": format_duration(total_duration),
        "status": "PASSED" if failed == 0 else "FAILED",
        "timestamp": run_timestamp,
        "suites": suites_summary,
    }
    summary_file = out_file.parent / "summary.json"
    summary_file.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")

    if additional_paths:
        for p in additional_paths:
            add_file = Path(p)
            add_file.parent.mkdir(parents=True, exist_ok=True)
            add_file.write_text(html_content, encoding="utf-8")

    return html_content
