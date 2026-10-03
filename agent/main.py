from agent.logger import logger
from agent.config import config

def main():
    logger.info("Agent started")
    logger.info(f"Running with AUTO_SUBMIT={config.AUTO_SUBMIT}")
    logger.info("Phase 1: Basic setup and logging initialized.")
    logger.info("Agent completed")

if __name__ == "__main__":
    main()
