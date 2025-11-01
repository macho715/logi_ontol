#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Screenshot script for unified logistics network visualization
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time


def screenshot_network(
    html_file: str, output_file: str, width: int = 1920, height: int = 1080
):
    """Capture screenshot of network visualization"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})

        # Load the HTML file
        html_path = Path(html_file).resolve()
        page.goto(f"file://{html_path}")

        # Wait for network to stabilize
        page.wait_for_timeout(5000)

        # Take screenshot
        page.screenshot(path=output_file, full_page=True)
        browser.close()

        print(f"[OK] Screenshot saved: {output_file}")


def main():
    """Generate screenshot for unified network"""
    print("=" * 60)
    print("Unified Network Screenshot")
    print("=" * 60)

    # Create output directory
    output_dir = Path("reports/analysis/image/UNIFIED_NETWORK")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Screenshot unified network
    unified_html = "UNIFIED_LOGISTICS_NETWORK_v12_HVDC.html"
    unified_png = output_dir / "UNIFIED_LOGISTICS_NETWORK_v12_HVDC.png"

    if Path(unified_html).exists():
        screenshot_network(unified_html, str(unified_png))
    else:
        print(f"[ERROR] {unified_html} not found")

    print("\n" + "=" * 60)
    print("[SUCCESS] Screenshot generated!")
    print(f"  - {unified_png}")
    print("=" * 60)


if __name__ == "__main__":
    main()
