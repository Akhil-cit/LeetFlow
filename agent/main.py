from agent.logger import logger
from agent.config import config
from agent.browser import BrowserContext
from agent.leetcode import LeetCode
from agent.problem_parser import ProblemParser
from agent.solver import AISolver
from agent.storage import Storage
from agent.notifier import Notifier

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    
    storage = Storage()
    notifier = Notifier()
    
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
    
    # --- PURE API METHOD ---
    from agent.api_submit import LeetCodeAPI
    
    api = LeetCodeAPI(config.LEETCODE_SESSION)
    if not api.check_auth():
        logger.error("Halting agent. The pure API method still hit the IP-Mismatch block.")
        return
        
    problem_slug = problem['link'].strip('/').split('/')[-1]
    
    # Phase 10: AI Debugging Loop
    MAX_ATTEMPTS = 3
    attempt = 1
    
    while attempt <= MAX_ATTEMPTS:
        logger.info(f"--- Attempt {attempt} of {MAX_ATTEMPTS} ---")
        
        # Phase 13: Submission Control (skip test, go straight to submit)
        if config.AUTO_SUBMIT:
            submit_result = api.submit_solution(problem_slug, problem['id'], solution['code'])
            
            if submit_result == "Accepted":
                logger.info("🎉 Full submission ACCEPTED! Problem solved!")
                storage.log_result(problem, attempt, "Submitted: Accepted")
                notifier.send_notification(problem, attempt, "Submitted: Accepted")
                break
            else:
                logger.warning(f"Submission failed with: {submit_result}. AI will retry...")
                if attempt == MAX_ATTEMPTS:
                    logger.error("Max attempts reached. Submission failed.")
                    storage.log_result(problem, attempt, f"Submitted: {submit_result}")
                    notifier.send_notification(problem, attempt, f"Submitted: {submit_result}")
                    break
                solution = solver.debug(problem, solution['code'], f"Submission failed: {submit_result}", attempt)
                if not solution or not solution['code']:
                    break
                attempt += 1
        else:
            logger.info("AUTO_SUBMIT disabled. Skipping final submission.")
            break
            
    logger.info("Phase 10: AI debugging loop completed.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
