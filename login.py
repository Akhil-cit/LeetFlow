import os
import time
from playwright.sync_api import sync_playwright

print("==========================================")
print("   LeetCode Persistent Login Helper")
print("==========================================")
print("This will open a special browser window.")
print("1. Log in to your LeetCode account manually.")
print("2. Solve any captchas or Cloudflare checks.")
print("3. Once you see your profile icon, simply CLOSE the browser.")
print("The agent will remember your session forever!")
print("==========================================")

user_data_dir = os.path.join(os.getcwd(), "data", "browser_profile")
os.makedirs(user_data_dir, exist_ok=True)

with sync_playwright() as p:
    try:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel="chrome",
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
    except Exception as e:
        print(f"Failed to launch Chrome. Falling back to Chromium... ({e})")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        
    page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
    page.goto("https://leetcode.com/accounts/login/")
    
    print("\nWaiting for you to close the browser...")
    
    # Keep the script running until the user closes the browser
    try:
        while len(browser.pages) > 0:
            time.sleep(1)
    except Exception:
        pass
        
print("Browser closed! Your session has been saved permanently.")
print("You NEVER have to copy the LEETCODE_SESSION cookie to .env again!")
