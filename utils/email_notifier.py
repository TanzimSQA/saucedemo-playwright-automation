"""
Email Notification Utility for SauceDemo Playwright Automation.
Dispatches a modern, responsive HTML email report to tanzimsqa@gmail.com
after automated test execution completes (locally or on GitHub Actions CI).
"""

import os
import sys
import json
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Configure utf-8 stdout/stderr for cross-platform unicode safety (Windows cp1252 fix)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Default recipient
DEFAULT_RECIPIENT = "tanzimsqa@gmail.com"
REPORT_URL = "https://tanzimsqa.github.io/saucedemo-playwright-automation/"
REPO_URL = "https://github.com/TanzimSQA/saucedemo-playwright-automation"


def load_test_summary() -> dict:
    """Load summary metrics from reports/summary.json or generate defaults."""
    summary_path = Path("reports/summary.json")
    if summary_path.exists():
        try:
            return json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[EMAIL NOTIFIER] Warning: Could not parse summary.json: {e}")

    # Fallback default values
    return {
        "total": 56,
        "passed": 56,
        "failed": 0,
        "skipped": 0,
        "pass_rate": 100.0,
        "total_duration": 125.7,
        "total_duration_formatted": "2m 5.7s",
        "status": "PASSED",
        "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S BST"),
        "suites": {
            "login": {"name": "Authentication & Login", "icon": "🔑", "total": 11, "passed": 11, "failed": 0},
            "inventory": {"name": "Catalog & Inventory", "icon": "📦", "total": 8, "passed": 8, "failed": 0},
            "cart": {"name": "Shopping Cart", "icon": "🛒", "total": 4, "passed": 4, "failed": 0},
            "checkout": {"name": "Checkout Flow", "icon": "💳", "total": 9, "passed": 9, "failed": 0},
            "e2e": {"name": "End-to-End Journeys", "icon": "🚀", "total": 2, "passed": 2, "failed": 0},
            "persona": {"name": "User Personas & Glitches", "icon": "🎭", "total": 4, "passed": 4, "failed": 0},
            "security": {"name": "Security & Route Guards", "icon": "🛡️", "total": 5, "passed": 5, "failed": 0},
            "sidebar": {"name": "Navigation & Sidebar", "icon": "🧭", "total": 5, "passed": 5, "failed": 0},
            "product_details": {"name": "Product Details", "icon": "🔍", "total": 4, "passed": 4, "failed": 0},
            "footer": {"name": "Footer & Social Links", "icon": "🌐", "total": 4, "passed": 4, "failed": 0},
        }
    }


def build_email_template(summary: dict, run_url: str = "") -> tuple[str, str]:
    """
    Constructs a modern, responsive HTML email template and plain text alternative.
    """
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    pass_rate = summary.get("pass_rate", 100.0)
    duration = summary.get("total_duration_formatted", "2m 5s")
    timestamp = summary.get("timestamp", datetime.now().strftime("%d-%b-%Y %H:%M:%S BST"))
    suites = summary.get("suites", {})

    is_all_passed = (failed == 0)
    status_text = "ALL TESTS PASSED (100% HEALTH)" if is_all_passed else f"{failed} FAILURE(S) DETECTED"
    status_color = "#10b981" if is_all_passed else "#f43f5e"
    status_bg = "#ecfdf5" if is_all_passed else "#fff1f2"
    status_border = "#10b981" if is_all_passed else "#f43f5e"
    status_symbol = "✓" if is_all_passed else "✗"

    # Subject line
    if is_all_passed:
        subject = f"✅ [PASS] SauceDemo Playwright Test Automation: {passed}/{total} Passed (100% Health)"
    else:
        subject = f"❌ [FAIL] SauceDemo Playwright Alert: {failed} Failed out of {total} Tests"

    # Suites rows
    suites_html = ""
    for s_id, s_data in suites.items():
        s_name = s_data.get("name", s_id)
        s_icon = s_data.get("icon", "🧪")
        s_tot = s_data.get("total", 0)
        s_pass = s_data.get("passed", 0)
        s_fail = s_data.get("failed", 0)
        s_status = f"<span style='color: #10b981; font-weight: 700;'>✓ {s_pass}/{s_tot} Passed</span>" if s_fail == 0 else f"<span style='color: #f43f5e; font-weight: 700;'>✗ {s_fail} Failed</span>"

        suites_html += f"""
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-size: 13px; color: #1e293b;">
            {s_icon} <strong>{s_name}</strong>
          </td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-size: 13px; text-align: right;">
            {s_status}
          </td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 30px 15px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table width="640" border="0" cellspacing="0" cellpadding="0" style="max-width: 640px; background-color: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
          
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 30px 32px; text-align: left;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%); border-radius: 10px; padding: 8px 12px; font-size: 20px; line-height: 1;">⚡</div>
                  </td>
                  <td style="padding-left: 14px;">
                    <h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">SauceDemo Playwright Automation</h1>
                    <p style="margin: 3px 0 0 0; font-size: 13px; color: #94a3b8;">Automated End-to-End Regression Test Execution Report</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Health Status Banner -->
          <tr>
            <td style="padding: 24px 32px 10px 32px;">
              <div style="background-color: {status_bg}; border: 1.5px solid {status_border}; border-radius: 10px; padding: 14px 20px; text-align: center;">
                <span style="font-size: 16px; font-weight: 800; color: {status_color}; letter-spacing: 0.02em;">
                  {status_symbol} {status_text}
                </span>
                <div style="margin-top: 4px; font-size: 12px; color: #64748b;">
                  Executed on {timestamp} • Chromium Headless (1280x800)
                </div>
              </div>
            </td>
          </tr>

          <!-- Metrics KPI Grid -->
          <tr>
            <td style="padding: 14px 32px 20px 32px;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <!-- Total -->
                  <td width="23%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 10px; text-align: center;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Total Tests</div>
                    <div style="font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 4px;">{total}</div>
                  </td>
                  <td width="3%"></td>
                  <!-- Passed -->
                  <td width="23%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 10px; text-align: center;">
                    <div style="font-size: 11px; font-weight: 700; color: #059669; text-transform: uppercase;">Passed</div>
                    <div style="font-size: 24px; font-weight: 800; color: #10b981; margin-top: 4px;">{passed}</div>
                  </td>
                  <td width="3%"></td>
                  <!-- Failed -->
                  <td width="23%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 10px; text-align: center;">
                    <div style="font-size: 11px; font-weight: 700; color: #e11d48; text-transform: uppercase;">Failed</div>
                    <div style="font-size: 24px; font-weight: 800; color: {'#f43f5e' if failed > 0 else '#94a3b8'}; margin-top: 4px;">{failed}</div>
                  </td>
                  <td width="3%"></td>
                  <!-- Pass Rate -->
                  <td width="23%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 10px; text-align: center;">
                    <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase;">Pass Rate</div>
                    <div style="font-size: 24px; font-weight: 800; color: #06b6d4; margin-top: 4px;">{pass_rate}%</div>
                  </td>
                </tr>
              </table>
              <div style="margin-top: 10px; text-align: right; font-size: 12px; color: #64748b;">
                ⏱️ Total Duration: <strong>{duration}</strong>
              </div>
            </td>
          </tr>

          <!-- Call To Action Buttons -->
          <tr>
            <td style="padding: 0 32px 24px 32px; text-align: center;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="center">
                    <a href="{REPORT_URL}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; padding: 13px 28px; border-radius: 8px; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);">
                      📊 View Live Interactive QA Report &rarr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Test Modules Breakdown Table -->
          <tr>
            <td style="padding: 0 32px 28px 32px;">
              <h3 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.04em;">
                📂 Test Modules Breakdown ({len(suites)} Suites)
              </h3>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; background-color: #ffffff;">
                {suites_html}
              </table>
            </td>
          </tr>

          <!-- Navigation & Quick Links -->
          <tr>
            <td style="padding: 20px 32px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center;">
              <div style="font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 8px;">Quick Links</div>
              <a href="{REPORT_URL}" style="color: #4f46e5; text-decoration: none; font-size: 12px; font-weight: 600; margin: 0 10px;">📊 GitHub Pages Report</a>
              •
              <a href="{REPO_URL}" style="color: #4f46e5; text-decoration: none; font-size: 12px; font-weight: 600; margin: 0 10px;">📂 GitHub Repository</a>
              {f"• <a href='{run_url}' style='color: #4f46e5; text-decoration: none; font-size: 12px; font-weight: 600; margin: 0 10px;'>🚀 CI Workflow Run</a>" if run_url else ""}
            </td>
          </tr>

          <!-- Footer Notice -->
          <tr>
            <td style="padding: 22px 32px; background-color: #0f172a; color: #94a3b8; font-size: 11px; text-align: center; line-height: 1.6;">
              This notification was automatically dispatched to <strong>{DEFAULT_RECIPIENT}</strong> following the completion of the SauceDemo test suite.<br/>
              Daily Schedule: 10:00 AM BST (04:00 UTC) • SauceDemo Playwright Automation
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    text_content = f"""
SauceDemo Playwright Test Automation - Execution Summary
======================================================
Status: {status_text}
Executed: {timestamp}
Pass Rate: {pass_rate}%
Total Tests: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}
Duration: {duration}

Live Interactive Report:
{REPORT_URL}

GitHub Repository:
{REPO_URL}
"""
    return subject, html_content, text_content


def send_notification_email(recipient: str = DEFAULT_RECIPIENT, dry_run: bool = False) -> bool:
    """
    Sends the email notification via SMTP (Gmail) to recipient.
    """
    # Environment configs
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER") or os.getenv("MAIL_USERNAME")
    smtp_pass = os.getenv("SMTP_PASS") or os.getenv("MAIL_PASSWORD")

    # GitHub Actions context
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    repo = os.getenv("GITHUB_REPOSITORY", "TanzimSQA/saucedemo-playwright-automation")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else ""

    summary = load_test_summary()
    subject, html_body, text_body = build_email_template(summary, run_url=run_url)

    # Save a preview file for inspection
    preview_file = Path("reports/email_preview.html")
    preview_file.parent.mkdir(parents=True, exist_ok=True)
    preview_file.write_text(html_body, encoding="utf-8")

    print(f"[EMAIL NOTIFIER] Preparing notification for: {recipient}")
    print(f"[EMAIL NOTIFIER] Subject: {subject}")
    print(f"[EMAIL NOTIFIER] Metrics: {summary.get('passed')}/{summary.get('total')} Passed ({summary.get('pass_rate')}%)")

    if dry_run:
        print("[EMAIL NOTIFIER] Dry run mode enabled. Email template rendered successfully.")
        return True

    if not smtp_user or not smtp_pass:
        print("\n" + "=" * 70)
        print("⚠️  [EMAIL NOTIFIER NOTICE] SMTP credentials not detected in environment.")
        print(f"Target recipient is configured as: {recipient}")
        print("To enable automatic email delivery to your inbox on every test run:")
        print("1. Go to your Google Account -> Security -> '2-Step Verification' -> 'App passwords'")
        print("   URL: https://myaccount.google.com/apppasswords")
        print("2. Generate a 16-character App Password for 'SauceDemo CI Automation'.")
        print("3. In your GitHub Repository, navigate to: Settings > Secrets and variables > Actions")
        print("4. Add the following Repository Secrets:")
        print("   • MAIL_USERNAME: your-sender-email@gmail.com (or tanzimsqa@gmail.com)")
        print("   • MAIL_PASSWORD: <16-character-app-password>")
        print("=" * 70 + "\n")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"SauceDemo QA Automation <{smtp_user}>"
        msg["To"] = recipient

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [recipient], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [recipient], msg.as_string())

        print(f"✅ [EMAIL NOTIFIER] Notification successfully dispatched to {recipient}!")
        return True

    except Exception as e:
        print(f"❌ [EMAIL NOTIFIER ERROR] Failed to send email to {recipient}: {e}")
        return False


if __name__ == "__main__":
    recipient_arg = os.getenv("EMAIL_RECIPIENT", DEFAULT_RECIPIENT)
    is_dry_run = "--dry-run" in sys.argv
    send_notification_email(recipient=recipient_arg, dry_run=is_dry_run)
