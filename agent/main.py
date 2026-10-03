from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    with BrowserContext() as page:
        logger.info("Navigating to test page...")
        page.goto("https://example.com")
        logger.info(f"Page title: {page.title()}")
        
    logger.info("Phase 3: Playwright installed and tested.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
