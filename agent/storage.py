import json
import os
from datetime import datetime
from agent.logger import logger

class Storage:
    def __init__(self, filepath="data/history.json"):
        self.filepath = filepath
        self._ensure_exists()

    def _ensure_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def load_history(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_history(self, history):
        with open(self.filepath, 'w') as f:
            json.dump(history, f, indent=4)

    def is_already_solved_today(self, problem_id):
        history = self.load_history()
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        for record in history:
            if record.get('date') == today and record.get('id') == problem_id:
                if "Accepted" in record.get('result', ''):
                    return True
        return False

    def log_result(self, problem, attempts, result_status):
        history = self.load_history()
        today = datetime.utcnow().strftime('%Y-%m-%d')
        timestamp = datetime.utcnow().isoformat()
        
        record = {
            "date": today,
            "timestamp": timestamp,
            "id": problem['id'],
            "title": problem['title'],
            "attempts": attempts,
            "result": result_status
        }
        
        history.append(record)
        self.save_history(history)
        logger.info(f"Result saved to {self.filepath}")
