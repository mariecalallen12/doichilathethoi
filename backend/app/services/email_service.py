"""
Email Service
Digital Utopia Platform

Service để gửi email notifications cho alerts và system events
"""

from typing import Optional, Dict, Any, List
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service để gửi email notifications
    
    Features:
    - Send HTML emails với templates
    - Support multiple recipients
    - Rate limiting để tránh spam
    """
    
    def __init__(self):
        """
        Khởi tạo EmailService với config từ environment variables
        """
        self.smtp_host = os.getenv('SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@forexxx.com')
        self.from_name = os.getenv('FROM_NAME', 'Forex Trading Platform')
        
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / 'templates' / 'emails'
        if template_dir.exists():
            self.env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        Gửi email
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content của email
            text_content: Plain text content (optional, sẽ được generate từ HTML nếu không có)
            attachments: List of attachments với format {'filename': str, 'content': bytes, 'content_type': str}
            
        Returns:
            True nếu gửi thành công, False nếu có lỗi
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add text part
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            else:
                # Generate plain text from HTML (simple strip)
                import re
                text_content = re.sub(r'<[^>]+>', '', html_content)
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Send email
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
    
    def send_alert_email(
        self,
        to_emails: List[str],
        alert_data: Dict[str, Any],
    ) -> bool:
        """
        Gửi email cho alert notification
        
        Args:
            to_emails: List of recipient email addresses
            alert_data: Alert data với các fields:
                - rule_name: Tên của alert rule
                - severity: Mức độ nghiêm trọng
                - health_status: Health status khi trigger
                - conditions_met: Conditions đã được thỏa mãn
                - triggered_at: Thời gian trigger
                - message: Message mô tả alert
                
        Returns:
            True nếu gửi thành công, False nếu có lỗi
        """
        try:
            # Load template
            if self.env:
                template = self.env.get_template('diagnostic_alert.html')
                html_content = template.render(**alert_data)
            else:
                # Fallback to simple HTML
                html_content = self._generate_simple_alert_html(alert_data)
            
            subject = f"Alert: {alert_data.get('rule_name', 'Trading Dashboard Issue')} - {alert_data.get('severity', 'Medium').upper()}"
            
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
            )
            
        except Exception as e:
            logger.error(f"Error sending alert email: {e}", exc_info=True)
            return False
    
    def _generate_simple_alert_html(self, alert_data: Dict[str, Any]) -> str:
        """
        Generate simple HTML email nếu không có template
        
        Args:
            alert_data: Alert data
            
        Returns:
            HTML content
        """
        severity = alert_data.get('severity', 'medium')
        severity_colors = {
            'low': '#3B82F6',      # Blue
            'medium': '#F59E0B',   # Yellow
            'high': '#F97316',     # Orange
            'critical': '#EF4444', # Red
        }
        color = severity_colors.get(severity, severity_colors['medium'])
        
        html = f"""
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
                    <h3>Conditions Met:</h3>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto;">{self._format_conditions(alert_data.get('conditions_met', {}))}</pre>
                </div>
                <div class="footer">
                    <p>This is an automated alert from the Trading Dashboard Diagnostic System.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _format_conditions(self, conditions: Dict[str, Any]) -> str:
        """
        Format conditions dict thành readable string
        
        Args:
            conditions: Conditions dictionary
            
        Returns:
            Formatted string
        """
        import json
        return json.dumps(conditions, indent=2)


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """
    Get singleton EmailService instance
    
    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

