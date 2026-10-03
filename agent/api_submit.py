import requests
import json
import time
from agent.logger import logger

class LeetCodeAPI:
    def __init__(self, session_cookie):
        self.session = requests.Session()
        self.session.cookies.set("LEETCODE_SESSION", session_cookie, domain=".leetcode.com")
        self.base_url = "https://leetcode.com"
        
        # Get a fresh CSRF token
        logger.info("Initializing API session and fetching CSRF token...")
        res = self.session.get("https://leetcode.com/")
        self.csrf_token = self.session.cookies.get("csrftoken")
        
        if not self.csrf_token:
            logger.warning("Could not get CSRF token from homepage. Session might be invalid.")
            
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://leetcode.com/",
            "x-csrftoken": self.csrf_token,
            "Content-Type": "application/json"
        })

    def check_auth(self):
        query = '{ userStatus { username isSignedIn } }'
        res = self.session.post('https://leetcode.com/graphql', json={'query': query})
        data = res.json().get('data', {}).get('userStatus', {})
        if data.get('isSignedIn'):
            logger.info(f"API Auth successful! Logged in as: {data.get('username')}")
            return True
        logger.error("API Auth failed. Session cookie is likely expired due to IP mismatch.")
        return False

    def submit_solution(self, problem_slug, question_id, code, lang="cpp"):
        logger.info(f"Submitting solution to {problem_slug} via API...")
        submit_url = f"https://leetcode.com/problems/{problem_slug}/submit/"
        
        self.session.headers.update({
            "Referer": f"https://leetcode.com/problems/{problem_slug}/"
        })
        
        payload = {
            "lang": lang,
            "question_id": question_id,
            "typed_code": code
        }
        
        res = self.session.post(submit_url, json=payload)
        
        if res.status_code != 200:
            logger.error(f"Submission failed with HTTP {res.status_code}: {res.text}")
            return "API Error"
            
        submission_id = res.json().get("submission_id")
        if not submission_id:
            logger.error(f"Failed to get submission ID: {res.text}")
            return "API Error"
            
        logger.info(f"Submission successful! ID: {submission_id}. Polling for results...")
        return self.poll_submission(submission_id)
        
    def poll_submission(self, submission_id):
        check_url = f"https://leetcode.com/submissions/detail/{submission_id}/check/"
        
        for _ in range(30):
            time.sleep(2)
            res = self.session.get(check_url)
            data = res.json()
            state = data.get("state")
            
            if state == "SUCCESS":
                status = data.get("status_msg")
                logger.info(f"Submission result: {status}")
                return status
            elif state != "PENDING":
                logger.info(f"Submission finished with state: {state}")
                return state
                
            logger.info("Still pending...")
            
        return "Timeout"
