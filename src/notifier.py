from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import requests


class Notifier:
    """Supports Telegram and SMTP notifications."""

    def __init__(
        self,
        telegram_bot_token: str | None = None,
        telegram_chat_id: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        email_from: str | None = None,
        email_to: str | None = None,
    ) -> None:
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_from = email_from
        self.email_to = email_to

    def send(self, message: str) -> None:
        sent_any = False

        if self.telegram_bot_token and self.telegram_chat_id:
            self._send_telegram(message)
            sent_any = True

        if all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password, self.email_from, self.email_to]):
            self._send_email(message)
            sent_any = True

        if not sent_any:
            raise RuntimeError(
                "No delivery channel configured. Provide Telegram credentials and/or SMTP settings."
            )

    def _send_telegram(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        resp = requests.post(
            url,
            json={
                "chat_id": self.telegram_chat_id,
                "text": message,
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        resp.raise_for_status()

    def _send_email(self, message: str) -> None:
        assert self.email_from and self.email_to and self.smtp_host and self.smtp_port and self.smtp_user and self.smtp_password
        mime = MIMEText(message)
        mime["Subject"] = "Daily News Digest: Tech + AI + Jobs + Software"
        mime["From"] = self.email_from
        mime["To"] = self.email_to

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as client:
            client.starttls()
            client.login(self.smtp_user, self.smtp_password)
            client.sendmail(self.email_from, [self.email_to], mime.as_string())
