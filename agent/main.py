from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext
from agent.leetcode import LeetCode

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    with BrowserContext() as page:
        lc = LeetCode(page)
        
        # Phase 5: Authentication
        success = lc.login(config.LEETCODE_USERNAME, config.LEETCODE_PASSWORD)
        if not success:
            logger.error("Halting agent due to login failure.")
            return
            
        lc.goto_home()
        
    logger.info("Phase 5: Authentication implemented securely.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
