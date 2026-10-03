from agent.logger import logger

class LeetCode:
    def __init__(self, page):
        self.page = page
        self.base_url = "https://leetcode.com"

    def login(self, username, password):
        logger.info("Attempting secure login...")
        if not username or not password:
            logger.error("Missing LeetCode credentials in secrets!")
            return False

        self.page.goto(self.base_url + "/accounts/login/", timeout=60000)
        
        try:
            # Wait for the login fields
            self.page.wait_for_selector("#id_login", timeout=15000)
            
            # Fill the credentials securely (Playwright doesn't print these to logs)
            self.page.fill("#id_login", username)
            self.page.fill("#id_password", password)
            
            # Click sign in
            self.page.click("button#signin_btn")
            
            # Wait for the page to navigate indicating a successful login
            # We wait for the navbar profile icon or a general post-login selector
            self.page.wait_for_load_state("networkidle", timeout=15000)
            logger.info("Authentication successful!")
            return True
        except Exception as e:
            logger.error(f"Authentication failed (Possibly Cloudflare block or wrong credentials).")
            return False

    def goto_home(self):
        logger.info("Navigating to LeetCode homepage...")
        self.page.goto(self.base_url, timeout=60000)
        self.page.wait_for_load_state("domcontentloaded")
        logger.info(f"Successfully loaded: {self.page.title()}")

    def insert_code(self, code):
        logger.info("Inserting generated C++ code into the LeetCode editor...")
        
        try:
            # Focus the Monaco Editor
            editor_selector = ".view-lines"
            self.page.wait_for_selector(editor_selector, timeout=15000)
            self.page.click(editor_selector)
            
            # Select all existing code and delete it
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Meta+A") # For Mac compatibility if ever run on mac runner
            self.page.keyboard.press("Backspace")
            
            # Paste the generated code
            self.page.keyboard.insert_text(code)
            
            logger.info("Code inserted successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to insert code: {e}")
            return False

    def test_solution(self):
        logger.info("Clicking the 'Run' button to test the solution...")
        
        try:
            # Click the Run button
            run_btn = self.page.locator("button[data-e2e-locator='console-run-button']")
            if run_btn.count() == 0:
                run_btn = self.page.locator("button:has-text('Run')").first
                
            run_btn.click()
            
            logger.info("Waiting for execution results (this might take a few seconds)...")
            
            # We must wait until the result text appears and isn't 'Pending' or 'Judging'
            self.page.wait_for_function("""
                () => {
                    const el = document.querySelector("[data-e2e-locator='console-result']");
                    return el && el.innerText.trim().length > 0 && !el.innerText.includes("Pending") && !el.innerText.includes("Judging");
                }
            """, timeout=30000)
            
            result_locator = self.page.locator("[data-e2e-locator='console-result']")
            status_text = result_locator.text_content().strip()
            logger.info(f"Test Result Status: {status_text}")
            
            # Extract details (like stdout, errors, expected vs actual)
            # The general container usually holds the diff and compilation errors
            details_text = self.page.locator("div.font-menlo").text_content() if self.page.locator("div.font-menlo").count() > 0 else ""
            
            return {
                "status": status_text,
                "details": details_text
            }
        except Exception as e:
            logger.error(f"Failed to run code or read result: {e}")
            return {"status": "Execution Timeout/Error", "details": str(e)}

    def submit_solution(self):
        logger.info("Clicking the 'Submit' button for final submission...")
        try:
            submit_btn = self.page.locator("button[data-e2e-locator='console-submit-button']")
            if submit_btn.count() == 0:
                submit_btn = self.page.locator("button:has-text('Submit')").first
                
            submit_btn.click()
            
            # Wait for submission to process
            logger.info("Waiting 10 seconds for submission to register on LeetCode servers...")
            self.page.wait_for_timeout(10000)
            
            logger.info("Submission complete.")
            return True
        except Exception as e:
            logger.error(f"Failed to submit solution: {e}")
            return False
