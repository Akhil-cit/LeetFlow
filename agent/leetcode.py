from agent.logger import logger

class LeetCode:
    def __init__(self, page):
        self.page = page
        self.base_url = "https://leetcode.com"

    def login(self, session_cookie):
        logger.info("Attempting login via Session Cookie...")
        if not session_cookie:
            logger.error("Missing LEETCODE_SESSION cookie in secrets!")
            return False

        try:
            # Set the session cookie directly in the browser context
            self.page.context.add_cookies([
                {
                    "name": "LEETCODE_SESSION",
                    "value": session_cookie,
                    "domain": ".leetcode.com",
                    "path": "/"
                }
            ])
            
            # Go to homepage to verify
            self.page.goto(self.base_url, timeout=60000)
            self.page.wait_for_load_state("domcontentloaded")
            
            # Check if we are actually logged in by looking for the premium/profile navbar
            # If the sign-in button is still there, the cookie is invalid or expired
            if self.page.locator("a[href='/accounts/login/']").count() > 0:
                logger.error("Session cookie is invalid or expired! Still seeing Sign In button.")
                return False
                
            logger.info("Cookie Authentication successful!")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
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

    def set_language_cpp(self):
        """Ensure C++ is selected as the language."""
        try:
            # Look for language selector button
            lang_btn = self.page.locator("button.rounded.items-center:has-text('C++')")
            if lang_btn.count() > 0:
                logger.info("C++ already selected.")
                return
            
            # Try clicking the language dropdown
            dropdown = self.page.locator("[data-e2e-locator='code-lang-button']")
            if dropdown.count() == 0:
                dropdown = self.page.locator("button.rounded").filter(has_text=lambda t: any(lang in t for lang in ['Python', 'Java', 'C', 'Go', 'Rust']))
            if dropdown.count() > 0:
                dropdown.first.click()
                self.page.wait_for_timeout(500)
                cpp_option = self.page.locator("div[role='option']:has-text('C++'), li:has-text('C++')")
                if cpp_option.count() > 0:
                    cpp_option.first.click()
                    self.page.wait_for_timeout(500)
                    logger.info("Switched to C++.")
        except Exception as e:
            logger.info(f"Language switch skipped: {e}")

    def test_solution(self):
        logger.info("Clicking the 'Run' button to test the solution...")
        
        try:
            # Click the Run button - try multiple selectors
            run_btn = self.page.locator("button[data-e2e-locator='console-run-button']")
            if run_btn.count() == 0:
                run_btn = self.page.locator("button:has-text('Run Code'), button:has-text('Run')")
            run_btn.first.click()
            
            logger.info("Waiting for execution results (up to 60 seconds)...")
            
            # Wait for any result keyword to appear anywhere on the page
            # This is much more robust than relying on a single selector
            self.page.wait_for_function("""
                () => {
                    const body = document.body.innerText;
                    return body.includes('Accepted') ||
                           body.includes('Wrong Answer') ||
                           body.includes('Compile Error') ||
                           body.includes('Runtime Error') ||
                           body.includes('Time Limit Exceeded') ||
                           body.includes('Memory Limit Exceeded') ||
                           body.includes('Output') ||
                           body.includes('Expected');
                }
            """, timeout=60000)
            
            # Now extract the result - try multiple selectors
            status_text = ""
            
            # Try the official data-e2e locator first
            result_el = self.page.locator("[data-e2e-locator='console-result']")
            if result_el.count() > 0:
                status_text = result_el.first.text_content().strip()
            
            # Fallback: scan page for known result strings
            if not status_text:
                page_text = self.page.evaluate("() => document.body.innerText")
                for keyword in ["Accepted", "Wrong Answer", "Compile Error", "Runtime Error", "Time Limit Exceeded", "Memory Limit Exceeded"]:
                    if keyword in page_text:
                        status_text = keyword
                        break
            
            if not status_text:
                status_text = "Unknown Result"
                
            logger.info(f"Test Result Status: {status_text}")
            
            # Extract error details for the AI debugger
            details_text = ""
            try:
                details_text = self.page.evaluate("""
                    () => {
                        const els = document.querySelectorAll('.font-menlo, [class*="console-"], [class*="result-"]');
                        return Array.from(els).map(e => e.innerText).join('\\n');
                    }
                """)
            except:
                pass
            
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
            
            logger.info("Waiting for final submission result (up to 60 seconds)...")
            
            # Wait for the submission result - LeetCode shows a modal or updates the page
            self.page.wait_for_function("""
                () => {
                    const body = document.body.innerText;
                    return body.includes('Accepted') ||
                           body.includes('Wrong Answer') ||
                           body.includes('Compile Error') ||
                           body.includes('Runtime Error') ||
                           body.includes('Time Limit Exceeded') ||
                           body.includes('Memory Limit Exceeded');
                }
            """, timeout=60000)
            
            # Read the result
            page_text = self.page.evaluate("() => document.body.innerText")
            
            for keyword in ["Accepted", "Wrong Answer", "Compile Error", "Runtime Error", "Time Limit Exceeded", "Memory Limit Exceeded"]:
                if keyword in page_text:
                    logger.info(f"Submission result: {keyword}")
                    return keyword
                    
            return "Unknown"
        except Exception as e:
            logger.error(f"Failed to submit solution: {e}")
            return "Submission Error"
