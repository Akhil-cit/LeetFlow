from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext
from agent.leetcode import LeetCode
from agent.problem_parser import ProblemParser

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    # Phase 6: Extract Problem
    problem = ProblemParser.get_daily_challenge()
    if not problem:
        logger.error("Could not extract problem. Halting.")
        return
        
    logger.info(f"Daily Challenge: {problem['title']}")
    logger.info(f"C++ Signature:\n{problem['cpp_signature']}")
    
    with BrowserContext() as page:
        lc = LeetCode(page)
        
        # Phase 5: Authentication
        success = lc.login(config.LEETCODE_USERNAME, config.LEETCODE_PASSWORD)
        if not success:
            logger.error("Halting agent due to login failure.")
            return
            
        # Navigate directly to the extracted problem page
        logger.info(f"Navigating to problem page: {problem['link']}")
        page.goto(problem['link'], timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        
    logger.info("Phase 6: Problem extracted and navigated to editor.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
