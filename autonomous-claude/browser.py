#!/usr/bin/env python3
"""
Browser automation utilities for Autonomous Claude.
Handles screenshot capture and metadata tracking.
"""
import os
import json
from datetime import datetime
from typing import Dict, Optional

SCREENSHOT_DIR = "/autonomous-claude/data/screenshots"


class BrowserSession:
    """Manages browser automation with automatic screenshot capture."""

    def __init__(self):
        self.screenshot_dir = SCREENSHOT_DIR
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.current_url = None
        self.current_title = None

    def save_screenshot(self, action: str, screenshot_data: bytes = None,
                       url: str = None, title: str = None) -> str:
        """
        Save a screenshot and its metadata.

        Args:
            action: Description of the action taken (e.g., "click_button", "navigate_to_page")
            screenshot_data: PNG screenshot bytes (optional for testing)
            url: Current page URL
            title: Current page title

        Returns:
            Path to the saved screenshot
        """
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"{timestamp}_{action}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        # Save screenshot (if provided)
        if screenshot_data:
            with open(filepath, 'wb') as f:
                f.write(screenshot_data)
        else:
            # Create placeholder for testing
            with open(filepath, 'wb') as f:
                f.write(b'')  # Empty file as placeholder

        # Save metadata
        meta_filepath = filepath.replace('.png', '.meta')
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "url": url or self.current_url,
            "title": title or self.current_title,
            "action": action
        }

        with open(meta_filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Screenshot saved: {filename}")
        return filepath

    def record_action(self, action: str, url: str = None, title: str = None,
                     screenshot_data: bytes = None) -> Dict:
        """
        Record a browser action with screenshot and metadata.

        This should be called AFTER every browser action.

        Args:
            action: What action was performed
            url: Current page URL
            title: Current page title
            screenshot_data: Screenshot bytes

        Returns:
            Dictionary with filepath and metadata
        """
        if url:
            self.current_url = url
        if title:
            self.current_title = title

        filepath = self.save_screenshot(action, screenshot_data, url, title)

        return {
            "screenshot": filepath,
            "url": self.current_url,
            "title": self.current_title,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_recent_screenshots(self, limit: int = 10) -> list:
        """Get list of recent screenshots with metadata."""
        screenshots = []

        for filename in sorted(os.listdir(self.screenshot_dir), reverse=True):
            if not filename.endswith('.png'):
                continue

            if len(screenshots) >= limit:
                break

            filepath = os.path.join(self.screenshot_dir, filename)
            meta_filepath = filepath.replace('.png', '.meta')

            metadata = {}
            if os.path.exists(meta_filepath):
                with open(meta_filepath, 'r') as f:
                    metadata = json.load(f)

            screenshots.append({
                "filepath": filepath,
                "filename": filename,
                **metadata
            })

        return screenshots


# Usage example for Playwright
PLAYWRIGHT_EXAMPLE = """
# Example: Using with Playwright

from playwright.sync_api import sync_playwright
from browser import BrowserSession

browser_session = BrowserSession()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Navigate
    page.goto('https://example.com')
    screenshot = page.screenshot()
    browser_session.record_action(
        action='navigate_to_example',
        url=page.url,
        title=page.title(),
        screenshot_data=screenshot
    )

    # Click button
    page.click('button#submit')
    screenshot = page.screenshot()
    browser_session.record_action(
        action='click_submit_button',
        url=page.url,
        title=page.title(),
        screenshot_data=screenshot
    )

    browser.close()
"""


# Usage example for Puppeteer (via pyppeteer)
PUPPETEER_EXAMPLE = """
# Example: Using with Puppeteer (pyppeteer)

import asyncio
from pyppeteer import launch
from browser import BrowserSession

async def main():
    browser_session = BrowserSession()

    browser = await launch()
    page = await browser.newPage()

    # Navigate
    await page.goto('https://example.com')
    screenshot = await page.screenshot()
    browser_session.record_action(
        action='navigate_to_example',
        url=page.url,
        title=await page.title(),
        screenshot_data=screenshot
    )

    # Click button
    await page.click('button#submit')
    screenshot = await page.screenshot()
    browser_session.record_action(
        action='click_submit_button',
        url=page.url,
        title=await page.title(),
        screenshot_data=screenshot
    )

    await browser.close()

asyncio.run(main())
"""


if __name__ == "__main__":
    # Demo
    print("Testing browser screenshot system...")
    session = BrowserSession()

    # Simulate some actions
    session.record_action(
        action="navigate_to_homepage",
        url="https://example.com",
        title="Example Domain"
    )

    session.record_action(
        action="click_login_button",
        url="https://example.com/login",
        title="Login - Example Domain"
    )

    # Show recent screenshots
    recent = session.get_recent_screenshots(limit=5)
    print(f"\nRecent screenshots: {len(recent)}")
    for s in recent:
        print(f"  {s['filename']}: {s.get('action', 'unknown')} at {s.get('url', 'unknown')}")

    print("\n" + "="*60)
    print("PLAYWRIGHT EXAMPLE:")
    print("="*60)
    print(PLAYWRIGHT_EXAMPLE)

    print("\n" + "="*60)
    print("PUPPETEER EXAMPLE:")
    print("="*60)
    print(PUPPETEER_EXAMPLE)
