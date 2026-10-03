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
            # The editor usually contains the class 'view-lines'
            editor_selector = ".view-lines"
            self.page.wait_for_selector(editor_selector, timeout=15000)
            self.page.click(editor_selector)
            
            # Select all existing code and delete it
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Meta+A") # For Mac compatibility if ever run on mac runner
            self.page.keyboard.press("Backspace")
            
            # Paste the generated code
            # Playwright's insert_text is much faster and more reliable than type() for large blocks of code
            self.page.keyboard.insert_text(code)
            
            logger.info("Code inserted successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to insert code: {e}")
            return False
