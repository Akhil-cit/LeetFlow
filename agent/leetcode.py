from agent.logger import logger

class LeetCode:
    def __init__(self, page):
        self.page = page
        self.base_url = "https://leetcode.com"

    def login(self, session_cookie=None, username=None, password=None):
        logger.info("Attempting authentication...")

        # Strategy 1: If a session cookie is provided, try it first (fastest)
        if session_cookie:
            try:
                self.page.context.add_cookies([{
                    "name": "LEETCODE_SESSION",
                    "value": session_cookie,
                    "domain": ".leetcode.com",
                    "path": "/"
                }])
                self.page.goto(self.base_url, timeout=60000)
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(2000)
                
                # Confirm login by calling LeetCode's GraphQL "whoami" endpoint
                # This is the most reliable check - it returns the username if logged in
                whoami = self.page.evaluate("""
                    async () => {
                        const res = await fetch('https://leetcode.com/graphql', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: '{ userStatus { username isSignedIn } }'})
                        });
                        const data = await res.json();
                        return data?.data?.userStatus;
                    }
                """)
                logger.info(f"Auth check result: {whoami}")
                if whoami and whoami.get('isSignedIn'):
                    logger.info(f"Cookie Authentication successful! Logged in as: {whoami.get('username')}")
                    return True
                logger.warning("Session cookie is invalid or expired (not signed in). Falling back to credentials...")
            except Exception as e:
                logger.warning(f"Cookie auth failed: {e}. Falling back to credentials...")

        # Strategy 2: Use Playwright to fill the browser login form via homepage modal
        if username and password:
            try:
                logger.info("Attempting browser-based credential login...")
                
                # Go to homepage (avoids Cloudflare on the login page directly)
                self.page.goto("https://leetcode.com/", timeout=60000)
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(2000)

                # Click "Sign In" button on the navbar
                sign_in_link = self.page.locator("a[href*='login'], button:has-text('Sign in'), a:has-text('Sign in')")
                if sign_in_link.count() > 0:
                    sign_in_link.first.click()
                    self.page.wait_for_timeout(2000)

                # Try filling the email/username field with multiple selectors
                email_input = self.page.locator(
                    "input[name='email'], input[name='login'], input[type='email'], "
                    "input[placeholder*='Email' i], input[placeholder*='email' i], "
                    "input[autocomplete='username'], input[autocomplete='email']"
                ).first
                email_input.wait_for(timeout=15000)
                email_input.fill(username)
                self.page.wait_for_timeout(500)

                # Fill password
                password_input = self.page.locator("input[type='password']").first
                password_input.fill(password)
                self.page.wait_for_timeout(500)

                # Click submit
                submit_btn = self.page.locator(
                    "button[type='submit'], button:has-text('Sign in'), button:has-text('Log in')"
                ).first
                submit_btn.click()

                # Wait for redirect (login disappears)
                self.page.wait_for_timeout(5000)
                self.page.wait_for_load_state("domcontentloaded")

                # Confirm logged in
                if self.page.locator("a[href='/accounts/login/']").count() == 0:
                    logger.info("Browser credential login successful!")
                    return True
                else:
                    logger.error("Credential login failed — still seeing Sign In after submit.")
                    return False
            except Exception as e:
                logger.error(f"Browser credential login failed: {e}")
                return False

        logger.error("No valid authentication method available (no session cookie and no credentials).")
        return False

    def goto_home(self):
        logger.info("Navigating to LeetCode homepage...")
        self.page.goto(self.base_url, timeout=60000)
        self.page.wait_for_load_state("domcontentloaded")
        logger.info(f"Successfully loaded: {self.page.title()}")

    def insert_code(self, code):
        logger.info("Inserting generated C++ code into the LeetCode editor...")

        # Strategy 1: Direct Monaco JavaScript API (bypasses DOM entirely)
        try:
            escaped_code = code.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
            result = self.page.evaluate(f"""
                () => {{
                    try {{
                        const editors = monaco.editor.getEditors();
                        if (editors && editors.length > 0) {{
                            editors[0].setValue(`{escaped_code}`);
                            return 'success';
                        }}
                        return 'no_editors';
                    }} catch(e) {{
                        return 'error:' + e.message;
                    }}
                }}
            """)
            logger.info(f"Monaco API result: {result}")
            if result == 'success':
                logger.info("Code inserted successfully via Monaco API.")
                return True
            logger.warning(f"Monaco API returned: {result}. Trying DOM fallback...")
        except Exception as e:
            logger.warning(f"Monaco API failed: {e}. Trying DOM fallback...")

        # Strategy 2: DOM fallback — click editor and keyboard type
        try:
            editor_selector = ".view-lines"
            logger.info("Waiting for Monaco editor DOM element (up to 30s)...")
            self.page.wait_for_selector(editor_selector, timeout=30000)
            self.page.click(editor_selector)
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            self.page.keyboard.insert_text(code)
            logger.info("Code inserted successfully via DOM fallback.")
            return True
        except Exception as e:
            logger.error(f"Failed to insert code: {e}")
            return False

    def set_language_cpp(self):
        """Ensure C++ is selected as the language."""
        try:
            # If any button already says C++, we're done
            if self.page.locator("button:has-text('C++')").count() > 0:
                logger.info("C++ already selected.")
                return
            
            # Click the language dropdown (try different selectors)
            dropdown = self.page.locator("[data-e2e-locator='code-lang-button']")
            if dropdown.count() == 0:
                # Look for any language name button (Python3, Java, etc.)
                for lang in ['Python3', 'Python', 'Java', 'Go', 'Rust', 'C#']:
                    dropdown = self.page.locator(f"button:has-text('{lang}')")
                    if dropdown.count() > 0:
                        break

            if dropdown.count() > 0:
                dropdown.first.click()
                self.page.wait_for_timeout(800)
                cpp_option = self.page.locator("div[role='option']:has-text('C++'), li:has-text('C++')")
                if cpp_option.count() > 0:
                    cpp_option.first.click()
                    self.page.wait_for_timeout(800)
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
