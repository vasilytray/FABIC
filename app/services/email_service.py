# services/email_service.py
import smtplib
from email.mime.text import MIMEText
from fastapi import BackgroundTasks
from app.config import settings

# Инициализация конфигурации


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def send_verification_email(self, email: str, code: str):
        message = MIMEText(f"Your verification code: {code}")
        message["Subject"] = "Email Verification"
        message["From"] = self.settings.SMTP_USER
        message["To"] = email
        
        try:
            with smtplib.SMTP(self.settings.SMTP_HOST, self.settings.SMTP_PORT) as server:
                server.starttls()
                server.login(self.settings.SMTP_USER, self.settings.SMTP_PASSWORD)
                server.sendmail(self.settings.SMTP_USER, email, message.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")