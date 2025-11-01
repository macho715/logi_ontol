#!/usr/bin/env python3
"""
JPT71 Integrated Network Screenshot Script
"""

import os
from pathlib import Path


def capture_screenshot():
    try:
        from playwright.sync_api import sync_playwright

        html_file = Path("c:/logi_ontol/JPT71_INTEGRATED_NETWORK.html")
        output_file = Path(
            "c:/logi_ontol/reports/analysis/JPT71_INTEGRATED_NETWORK.png"
        )

        output_file.parent.mkdir(parents=True, exist_ok=True)

        html_url = f"file:///{html_file.as_posix()}"

        print(f"[INFO] Opening: {html_url}")
        print(f"[INFO] Saving to: {output_file}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(html_url)
            page.wait_for_timeout(5000)  # Wait for network stabilization
            page.screenshot(path=str(output_file), full_page=False, type="png")
            browser.close()

        print(f"[OK] Screenshot saved: {output_file}")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


if __name__ == "__main__":
    print("JPT71 Integrated Network Screenshot Tool")
    print("=" * 50)
    capture_screenshot()
