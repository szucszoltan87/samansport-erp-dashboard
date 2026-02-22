"""
Playwright automation script to test analytics search for product 4633.
Navigates the SamanSport ERP dashboard to the Analytics page and searches
for product code 4633.
"""
import os
import time

CHROMIUM_PATH = os.path.expanduser("~/.cache/ms-playwright/chromium-1194/chrome-linux/chrome")
APP_URL = "http://localhost:8501"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    page.screenshot(path=path)
    print(f"  [screenshot] {path}")


def run():
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        # ── 1. Open the app ────────────────────────────────────────────────────
        print("Step 1: Opening the app...")
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        # Wait for Streamlit to finish its initial render
        page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
        time.sleep(2)
        screenshot(page, "01_app_loaded")
        print("  App loaded successfully.")

        # ── 2. Click "Analitika" in the sidebar ───────────────────────────────
        print("Step 2: Navigating to Analitika (Analytics)...")
        # Sidebar buttons: "  Dashboard" and "  Analitika"
        analytics_btn = page.locator('[data-testid="stSidebar"] button', has_text="Analitika")
        analytics_btn.wait_for(state="visible", timeout=10000)
        screenshot(page, "02_before_click_analytics")
        analytics_btn.click()
        # Wait for page to re-render
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        screenshot(page, "03_analytics_page_loaded")
        print("  Analytics page loaded.")

        # ── 3. Find and interact with product selectbox ────────────────────────
        print("Step 3: Searching for product 4633...")
        # Streamlit selectbox is a combobox or a listbox
        # Try to find the product selector (Termék)
        try:
            # In Streamlit, selectbox input is often accessible by label
            product_select = page.locator('[data-testid="stSelectbox"]').first
            product_select.wait_for(state="visible", timeout=10000)
            screenshot(page, "04_product_selectbox_found")

            # Click to open the dropdown
            product_select.click()
            time.sleep(1)
            screenshot(page, "05_dropdown_opened")

            # Type the product code to search
            page.keyboard.type("4633")
            time.sleep(1)
            screenshot(page, "06_typed_4633")

            # Look for matching option in the dropdown list
            try:
                option = page.locator('[data-testid="stSelectboxVirtualDropdown"] li', has_text="4633").first
                option.wait_for(state="visible", timeout=5000)
                screenshot(page, "07_option_visible")
                option.click()
                time.sleep(1)
                screenshot(page, "08_product_selected")
                print("  Product 4633 selected from dropdown.")
            except PWTimeout:
                print("  No dropdown option found containing '4633' — product may not be in master list.")
                screenshot(page, "07_no_option_found")

        except PWTimeout:
            print("  Selectbox not found — taking screenshot for diagnosis.")
            screenshot(page, "04_no_selectbox")

        # ── 4. Final state ─────────────────────────────────────────────────────
        print("Step 4: Capturing final state...")
        time.sleep(2)
        screenshot(page, "09_final_state")
        print(f"\nDone. Screenshots saved to: {SCREENSHOTS_DIR}/")

        browser.close()


if __name__ == "__main__":
    run()
