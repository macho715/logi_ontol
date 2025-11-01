#!/usr/bin/env python3
"""
JPT71 Gantt Chart Screenshot Script
Automatically captures PNG screenshot of HTML gantt chart
"""

import os
import sys
from pathlib import Path


def install_playwright():
    """Install playwright if not available"""
    try:
        import playwright

        print("[OK] Playwright already installed")
        return True
    except ImportError:
        print("[INFO] Installing playwright...")
        os.system("pip install playwright")
        os.system("playwright install")
        return True


def capture_gantt_screenshot():
    """Capture screenshot of JPT71 gantt chart"""
    try:
        from playwright.sync_api import sync_playwright

        # File paths
        html_file = Path("c:/logi_ontol/reports/analysis/JPT71_gantt_timeline.html")
        output_dir = Path(
            "c:/logi_ontol/reports/analysis/image/JPT71_NETWORK_VISUALIZATION"
        )
        output_file = output_dir / "JPT71_gantt_chart.png"

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert to file URL
        html_url = f"file:///{html_file.as_posix()}"

        print(f"[INFO] Opening: {html_url}")
        print(f"[INFO] Saving to: {output_file}")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Set viewport for high quality
            page.set_viewport_size({"width": 1920, "height": 1080})

            # Navigate to HTML file
            page.goto(html_url)

            # Wait for content to load
            page.wait_for_timeout(2000)

            # Take full page screenshot
            page.screenshot(path=str(output_file), full_page=True, type="png")

            browser.close()

        print(f"[OK] Screenshot saved: {output_file}")
        return True

    except Exception as e:
        print(f"[ERROR] Error capturing screenshot: {e}")
        return False


def main():
    """Main execution function"""
    print("JPT71 Gantt Chart Screenshot Tool")
    print("=" * 50)

    # Check if HTML file exists
    html_file = Path("c:/logi_ontol/reports/analysis/JPT71_gantt_timeline.html")
    if not html_file.exists():
        print(f"[ERROR] HTML file not found: {html_file}")
        return False

    # Install playwright if needed
    if not install_playwright():
        print("[ERROR] Failed to install playwright")
        return False

    # Capture screenshot
    success = capture_gantt_screenshot()

    if success:
        print("\n[SUCCESS] Screenshot capture completed successfully!")
        print("[INFO] Check the image folder for the PNG file")
    else:
        print("\n[ERROR] Screenshot capture failed")

    return success


if __name__ == "__main__":
    main()
