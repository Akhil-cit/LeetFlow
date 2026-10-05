import os
from playwright.sync_api import sync_playwright
from agent.logger import logger
from agent.config import config

class BrowserContext:
    def __init__(self):
        self.playwright = None
        self.context = None
        self.page = None

    def __enter__(self):
        logger.info("Initializing Playwright persistent browser...")
        self.playwright = sync_playwright().start()
        
        user_data_dir = os.path.join(os.getcwd(), "data", "browser_profile")
        os.makedirs(user_data_dir, exist_ok=True)
        
        logger.info(f"Launching persistent browser (Headless: {config.HEADLESS})")
        
        try:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=config.HEADLESS,
                channel="chrome",  # Uses the real system Google Chrome (better for Cloudflare)
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        except Exception as e:
            logger.warning(f"Failed to launch with channel='chrome': {e}. Falling back to default chromium.")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=config.HEADLESS,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()
            
        return self.page

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing browser...")
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
