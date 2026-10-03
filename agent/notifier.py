import requests
from agent.logger import logger
from agent.config import config
from datetime import datetime

class Notifier:
    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID

    def send_notification(self, problem, attempts, result_status):
        if not self.bot_token or not self.chat_id:
            logger.info("Telegram notifications disabled (missing token or chat ID).")
            return

        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        
        if "Accepted" in result_status:
            emoji = "✅"
            status_text = "Accepted"
        else:
            emoji = "❌"
            status_text = f"Failed\nReason: {result_status}"

        auto_submit_status = "Enabled" if config.AUTO_SUBMIT else "Disabled"

        message = f"""🤖 *LeetCode Daily Agent*

Date: {date_str}
Problem: {problem['title']}
Attempts: {attempts}
Result: {emoji} {status_text}
Auto Submit: {auto_submit_status}"""

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully.")
            else:
                logger.error(f"Failed to send Telegram notification: {response.text}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
