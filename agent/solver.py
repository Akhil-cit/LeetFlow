import re
from google import genai
from agent.logger import logger
from agent.config import config

class AISolver:
    def __init__(self):
        self.api_key = config.AI_API_KEY
        if not self.api_key:
            logger.error("AI_API_KEY is missing in secrets!")
            self.client = None
        else:
            # We use Google's Gemini API because it has a very generous free tier.
            self.client = genai.Client(api_key=self.api_key)

    def solve(self, problem):
        logger.info("Sending problem to AI solver...")
        if not self.client:
            logger.error("Cannot solve without AI_API_KEY.")
            return None

        prompt = f"""
You are an expert C++ competitive programmer.
Solve the following LeetCode problem.

Title: {problem['title']}
Description: {problem['description_html']}

You MUST provide your response in the following exact format:

### Problem Understanding
(Briefly explain the problem)

### Algorithm
(Explain your approach)

### Time Complexity
(e.g., O(N))

### Space Complexity
(e.g., O(1))

### Final C++ Solution
```cpp
{problem['cpp_signature']}
    // your code here
}}
```

CRITICAL INSTRUCTIONS:
- You must use the exact provided C++ function signature.
- Do not invent APIs, constraints, or input formats.
- The C++ code block must be cleanly extractable.
"""
        
        try:
            # We use gemini-2.5-flash as it is fast, highly capable in coding, and in the free tier
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            
            raw_response = response.text
            logger.info("Solution generated successfully.")
            
            # Extract just the code from the markdown block
            code_match = re.search(r'```cpp\n(.*?)\n```', raw_response, re.DOTALL)
            if code_match:
                final_code = code_match.group(1).strip()
                logger.info("C++ code cleanly extracted from AI response.")
            else:
                logger.error("Failed to extract C++ code. The AI did not follow the formatting rules.")
                final_code = None
                
            return {
                "raw_response": raw_response,
                "code": final_code
            }
            
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return None

    def debug(self, problem, wrong_code, error_details, attempt):
        logger.info(f"Asking AI to debug code (Attempt {attempt})...")
        if not self.client:
            return None

        prompt = f"""
You are an expert C++ competitive programmer.
You previously wrote a solution for the following LeetCode problem, but it failed when tested.

Title: {problem['title']}
Description: {problem['description_html']}

### Your Previous Code:
```cpp
{wrong_code}
```

### The Error / Test Failure:
{error_details}

Please analyze the error and provide a corrected C++ solution.

You MUST provide your response in the following exact format:

### Bug Analysis
(Explain why it failed and how to fix it)

### Final C++ Solution
```cpp
{problem['cpp_signature']}
    // your corrected code here
}}
```

CRITICAL INSTRUCTIONS:
- You must use the exact provided C++ function signature.
- The C++ code block must be cleanly extractable.
"""
        try:
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            
            raw_response = response.text
            logger.info("Debugged solution generated successfully.")
            
            code_match = re.search(r'```cpp\n(.*?)\n```', raw_response, re.DOTALL)
            if code_match:
                final_code = code_match.group(1).strip()
            else:
                logger.error("Failed to extract C++ code from debug response.")
                final_code = None
                
            return {
                "raw_response": raw_response,
                "code": final_code
            }
        except Exception as e:
            logger.error(f"AI API call failed during debug: {e}")
            return None
