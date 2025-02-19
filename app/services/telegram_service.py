# services/telegram_service.py
from aiogram import Bot

class TelegramService:
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
    
    async def send_verification_code(self, chat_id: str, code: str):
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=f"Your phone verification code: {code}\nCode expires in 30 minutes."
            )
        except Exception as e:
            print(f"Error sending Telegram message: {e}")