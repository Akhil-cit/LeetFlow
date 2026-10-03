import requests
from agent.logger import logger

class ProblemParser:
    @staticmethod
    def get_daily_challenge():
        logger.info("Fetching daily challenge details via GraphQL...")
        query = """
        query questionOfToday {
            activeDailyCodingChallengeQuestion {
                link
                question {
                    questionId
                    title
                    content
                    codeSnippets {
                        lang
                        langSlug
                        code
                    }
                }
            }
        }
        """
        response = requests.post('https://leetcode.com/graphql', json={'query': query})
        
        if response.status_code != 200:
            logger.error(f"GraphQL request failed with status {response.status_code}")
            return None
            
        data = response.json().get('data', {}).get('activeDailyCodingChallengeQuestion')
        if not data:
            logger.error("Failed to parse daily challenge from GraphQL response.")
            return None
            
        question = data['question']
        
        # Extract C++ snippet specifically as requested
        cpp_snippet = next((s['code'] for s in question['codeSnippets'] if s['langSlug'] == 'cpp'), "")
        
        problem_details = {
            "link": "https://leetcode.com" + data['link'],
            "id": question['questionId'],
            "title": question['title'],
            "description_html": question['content'],
            "cpp_signature": cpp_snippet,
            "available_languages": [s['lang'] for s in question['codeSnippets']]
        }
        
        logger.info(f"Successfully extracted problem: {problem_details['title']}")
        return problem_details
