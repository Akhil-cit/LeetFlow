from agent.logger import logger

class LeetCode:
    def __init__(self, page):
        self.page = page
        self.base_url = "https://leetcode.com"

    def goto_home(self):
        logger.info("Navigating to LeetCode homepage...")
        # Using timeout=60000 to give the cloud runner plenty of time to load
        self.page.goto(self.base_url, timeout=60000)
        self.page.wait_for_load_state("domcontentloaded")
        logger.info(f"Successfully loaded: {self.page.title()}")
