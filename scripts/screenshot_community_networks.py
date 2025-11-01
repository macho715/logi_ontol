#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Screenshot script for community detection network visualizations
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
        page.wait_for_timeout(3000)

        # Take screenshot
        page.screenshot(path=output_file, full_page=True)
        browser.close()

        print(f"[OK] Screenshot saved: {output_file}")


def main():
    """Generate screenshots for both community detection versions"""
    print("=" * 60)
    print("Community Detection Network Screenshots")
    print("=" * 60)

    # Create output directory
    output_dir = Path("reports/analysis/image/COMMUNITY_DETECTION")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Screenshot Louvain version
    louvain_html = "JPT71_INTEGRATED_NETWORK_LOUVAIN.html"
    louvain_png = output_dir / "JPT71_LOUVAIN_COMMUNITIES.png"

    if Path(louvain_html).exists():
        screenshot_network(louvain_html, str(louvain_png))
    else:
        print(f"[ERROR] {louvain_html} not found")

    # Screenshot Leiden version
    leiden_html = "JPT71_INTEGRATED_NETWORK_LEIDEN.html"
    leiden_png = output_dir / "JPT71_LEIDEN_COMMUNITIES.png"

    if Path(leiden_html).exists():
        screenshot_network(leiden_html, str(leiden_png))
    else:
        print(f"[ERROR] {leiden_html} not found")

    print("\n" + "=" * 60)
    print("[SUCCESS] Screenshots generated!")
    print(f"  - {louvain_png}")
    print(f"  - {leiden_png}")
    print("=" * 60)


if __name__ == "__main__":
    main()
