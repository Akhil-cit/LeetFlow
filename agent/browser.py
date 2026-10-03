from playwright.sync_api import sync_playwright
from agent.logger import logger
from agent.config import config

class BrowserContext:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        logger.info("Initializing Playwright browser...")
        self.playwright = sync_playwright().start()
        
        # We use chromium as it is highly compatible with LeetCode
        logger.info(f"Launching browser (Headless: {config.HEADLESS})")
        self.browser = self.playwright.chromium.launch(
            headless=config.HEADLESS,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        
        # Set a realistic user agent to avoid being blocked
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.page = self.context.new_page()
        return self.page

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing browser...")
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
