from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext
from agent.leetcode import LeetCode
from agent.problem_parser import ProblemParser
from agent.solver import AISolver

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    # Phase 6: Extract Problem
    problem = ProblemParser.get_daily_challenge()
    if not problem:
        logger.error("Could not extract problem. Halting.")
        return
        
    logger.info(f"Daily Challenge: {problem['title']}")
    
    # Phase 7: AI Problem Solving
    solver = AISolver()
    solution = solver.solve(problem)
    
    if not solution or not solution['code']:
        logger.error("Failed to generate a valid solution. Halting.")
        return
        
    logger.info(f"Generated Code snippet (first 100 chars): {solution['code'][:100]}...")
    
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
        
        # Wait for the complex React app and editor to load
        page.wait_for_load_state("networkidle", timeout=30000)
        
        # Phase 8: Insert the AI-generated code
        success = lc.insert_code(solution['code'])
        if not success:
            logger.error("Failed to insert code into editor. Halting.")
            return
            
    logger.info("Phase 8: AI solution successfully pasted into the LeetCode editor!")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
