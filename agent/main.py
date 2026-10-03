from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext
from agent.leetcode import LeetCode

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    with BrowserContext() as page:
        lc = LeetCode(page)
        lc.goto_home()
        
    logger.info("Phase 4: LeetCode homepage loaded.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
