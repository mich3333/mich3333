#!/usr/bin/env python3
"""
Screenshot Generator for Autonomous Claude
צולם screenshots של הממשק
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def take_screenshots():
    """Take screenshots of the web interface."""

    print("🎬 Starting screenshot capture...")

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    # Create screenshots directory
    screenshots_dir = '/home/user/mich3333/screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)

    try:
        print("📦 Initializing browser...")
        driver = webdriver.Chrome(options=chrome_options)

        # Screenshot 1: Portfolio Landing Page
        print("\n📸 Screenshot 1: Portfolio Landing Page")
        driver.get('http://localhost:5000/')
        time.sleep(2)  # Wait for page to load
        screenshot_path = f'{screenshots_dir}/01-portfolio-landing.png'
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: {screenshot_path}")

        # Scroll down for more content
        print("\n📸 Screenshot 2: Portfolio Features Section")
        driver.execute_script("window.scrollTo(0, 800)")
        time.sleep(1)
        screenshot_path = f'{screenshots_dir}/02-portfolio-features.png'
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: {screenshot_path}")

        # Screenshot 3: Tech Stack
        print("\n📸 Screenshot 3: Portfolio Tech Stack")
        driver.execute_script("window.scrollTo(0, 1600)")
        time.sleep(1)
        screenshot_path = f'{screenshots_dir}/03-portfolio-tech-stack.png'
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: {screenshot_path}")

        # Screenshot 4: Dashboard
        print("\n📸 Screenshot 4: Dashboard Main")
        driver.get('http://localhost:5000/dashboard')
        time.sleep(2)
        screenshot_path = f'{screenshots_dir}/04-dashboard-main.png'
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: {screenshot_path}")

        # Full page screenshot
        print("\n📸 Screenshot 5: Full Portfolio Page")
        driver.get('http://localhost:5000/')
        time.sleep(2)

        # Get full page height
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        time.sleep(1)

        screenshot_path = f'{screenshots_dir}/05-portfolio-full-page.png'
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: {screenshot_path}")

        print("\n" + "="*60)
        print("✅ All screenshots captured successfully!")
        print("="*60)
        print(f"\n📁 Screenshots saved to: {screenshots_dir}/")
        print("\nFiles created:")
        for f in sorted(os.listdir(screenshots_dir)):
            if f.endswith('.png'):
                size = os.path.getsize(f'{screenshots_dir}/{f}') / 1024
                print(f"   - {f} ({size:.1f} KB)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTrying alternative method with Firefox...")

        # Try with Firefox as fallback
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--headless')

            driver = webdriver.Firefox(options=firefox_options)
            driver.get('http://localhost:5000/')
            time.sleep(2)

            screenshot_path = f'{screenshots_dir}/portfolio-firefox.png'
            driver.save_screenshot(screenshot_path)
            print(f"✅ Screenshot saved with Firefox: {screenshot_path}")

        except Exception as e2:
            print(f"❌ Firefox also failed: {e2}")
            print("\nNote: Install Chrome/Firefox driver:")
            print("  pip install selenium webdriver-manager")

    finally:
        if 'driver' in locals():
            driver.quit()
            print("\n🔒 Browser closed")

if __name__ == '__main__':
    print("="*60)
    print("📸 Autonomous Claude - Screenshot Generator")
    print("="*60)
    take_screenshots()
