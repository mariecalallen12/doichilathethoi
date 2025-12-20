"""
Email Service
Digital Utopia Platform

Service để gửi email notifications cho alerts và system events.

Ghi chú:
- Dùng config tập trung từ `app.core.config.get_settings()`
- Hỗ trợ HTML + text fallback, nhiều người nhận, và attachments cơ bản
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service để gửi email notifications.
    """

    def __init__(self):
        """
        Khởi tạo EmailService với config từ Settings.
        """
        settings = get_settings()

        self.smtp_host = settings.SMTP_HOST or "localhost"
        self.smtp_port = int(settings.SMTP_PORT or 587)
        self.smtp_user = settings.SMTP_USER or ""
        self.smtp_password = settings.SMTP_PASSWORD or ""
        # Backend config hiện không có SMTP_USE_TLS; mặc định bật TLS để an toàn
        self.smtp_use_tls = True

        self.from_email = settings.EMAILS_FROM_EMAIL or "noreply@digitalutopia.com"
        self.from_name = settings.EMAILS_FROM_NAME or "CMEETRADING"

        # Setup Jinja2 template environment (optional)
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if template_dir.exists():
            self.env: Optional[Environment] = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            self.env = None
            logger.warning(f"Email templates directory not found: {template_dir}")

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Gửi email qua SMTP.
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            else:
                # Simple HTML -> text fallback
                import re

                stripped = re.sub(r"<[^>]+>", "", html_content)
                msg.attach(MIMEText(stripped, "plain"))

            msg.attach(MIMEText(html_content, "html"))

            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{attachment["filename"]}"',
                    )
                    msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg, from_addr=self.from_email, to_addrs=to_emails)

            logger.info(f"Email sent successfully to {to_emails}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False

    def send_alert_email(self, to_emails: List[str], alert_data: Dict[str, Any]) -> bool:
        """
        Gửi email cho alert notification (dùng template nếu có).
        """
        try:
            if self.env:
                template = self.env.get_template("diagnostic_alert.html")
                html_content = template.render(**alert_data)
            else:
                html_content = self._generate_simple_alert_html(alert_data)

            subject = (
                f"Alert: {alert_data.get('rule_name', 'Trading Dashboard Issue')} - "
                f"{str(alert_data.get('severity', 'Medium')).upper()}"
            )

            return self.send_email(to_emails=to_emails, subject=subject, html_content=html_content)
        except Exception as e:
            logger.error(f"Error sending alert email: {e}", exc_info=True)
            return False

    def _generate_simple_alert_html(self, alert_data: Dict[str, Any]) -> str:
        severity = (alert_data.get("severity") or "medium").lower()
        severity_colors = {
            "low": "#3B82F6",
            "medium": "#F59E0B",
            "high": "#F97316",
            "critical": "#EF4444",
        }
        color = severity_colors.get(severity, severity_colors["medium"])

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .alert-box {{ background-color: #fff; border-left: 4px solid {color}; padding: 15px; margin: 15px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .severity-badge {{ display: inline-block; padding: 5px 10px; background-color: {color}; color: white; border-radius: 3px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Trading Dashboard Alert</h1>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <h2>{alert_data.get('rule_name', 'Alert Triggered')}</h2>
                        <p><strong>Severity:</strong> <span class="severity-badge">{severity.upper()}</span></p>
                        <p><strong>Health Status:</strong> {alert_data.get('health_status', 'Unknown')}</p>
                        <p><strong>Triggered At:</strong> {alert_data.get('triggered_at', 'N/A')}</p>
                        <p><strong>Message:</strong> {alert_data.get('message', 'An alert has been triggered')}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated alert from the Trading Dashboard Diagnostic System.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get singleton EmailService instance.
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


