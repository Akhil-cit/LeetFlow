from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext
from agent.leetcode import LeetCode
from agent.problem_parser import ProblemParser
from agent.solver import AISolver
from agent.storage import Storage

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    storage = Storage()
    
    # Phase 6: Extract Problem
    problem = ProblemParser.get_daily_challenge()
    if not problem:
        logger.error("Could not extract problem. Halting.")
        return
        
    logger.info(f"Daily Challenge: {problem['title']}")
    
    # Phase 11: Duplicate Protection
    if storage.is_already_solved_today(problem['id']):
        logger.info("This problem has already been successfully solved today! Exiting to save resources.")
        return
    
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
        
        # Phase 10: AI Debugging Loop
        MAX_ATTEMPTS = 3
        attempt = 1
        
        while attempt <= MAX_ATTEMPTS:
            logger.info(f"--- Attempt {attempt} of {MAX_ATTEMPTS} ---")
            
            # Phase 8: Insert the AI-generated code
            success = lc.insert_code(solution['code'])
            if not success:
                logger.error("Failed to insert code into editor. Halting.")
                return
                
            # Phase 9: Run code and read result
            result = lc.test_solution()
            logger.info(f"Code executed. Final Status: {result['status']}")
            
            if "Accepted" in result['status']:
                logger.info("Solution was accepted by tests!")
                storage.log_result(problem, attempt, result['status'])
                break
            else:
                if attempt == MAX_ATTEMPTS:
                    logger.error("Max attempts reached. Failed to solve the problem.")
                    storage.log_result(problem, attempt, result['status'])
                    break
                    
                logger.info(f"Code failed with status: {result['status']}. Requesting debug from AI...")
                solution = solver.debug(problem, solution['code'], result['details'], attempt)
                
                if not solution or not solution['code']:
                    logger.error("AI failed to provide a debugged solution. Halting.")
                    storage.log_result(problem, attempt, "Debug Generation Failed")
                    break
                    
                attempt += 1
                
    logger.info("Phase 10: AI debugging loop completed.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
