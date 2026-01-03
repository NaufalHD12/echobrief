import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_TLS
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

        # Setup Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader("app/templates/email"), autoescape=True
        )

    def _get_smtp_connection(self):
        """Get SMTP connection"""
        if self.use_tls:
            smtp = SMTP(self.smtp_host, self.smtp_port)
            smtp.starttls()
        else:
            smtp = SMTP_SSL(self.smtp_host, self.smtp_port)

        if self.smtp_username and self.smtp_password:
            smtp.login(self.smtp_username, self.smtp_password)

        return smtp

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        try:
            template = self.template_env.get_template(f"{template_name}.html")
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        """Send email synchronously"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with self._get_smtp_connection() as smtp:
                smtp.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.KOFI_URL}/reset-password?token={reset_token}"

        context = {
            "reset_url": reset_url,
            "token_expiry_minutes": settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
        }

        html_content = self._render_template("password_reset", context)
        text_content = f"""
        Password Reset Request

        You requested a password reset for your EchoBrief account.

        Click the following link to reset your password:
        {reset_url}

        This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.

        If you didn't request this password reset, please ignore this email.

        Best regards,
        EchoBrief Team
        """

        return self.send_email(
            to_email=to_email,
            subject="Reset Your EchoBrief Password",
            html_content=html_content,
            text_content=text_content,
        )

    def send_subscription_success_email(
        self,
        to_email: str,
        user_name: str,
        plan_type: str = "paid",
        amount: str | None = None,
    ) -> bool:
        """Send subscription success email"""
        context = {"user_name": user_name, "plan_type": plan_type, "amount": amount}

        html_content = self._render_template("subscription_success", context)
        text_content = f"""
        Payment Successful - Welcome to EchoBrief Premium!

        Hi {user_name},

        Thank you for your payment! Your subscription has been activated successfully.

        Plan: Premium ({plan_type})
        {"Amount: $" + amount if amount else ""}

        You now have access to all premium features including:
        - Unlimited podcast generations
        - Advanced topic customization
        - Priority processing

        Enjoy your premium experience!

        Best regards,
        EchoBrief Team
        """

        return self.send_email(
            to_email=to_email,
            subject="Payment Successful - Welcome to EchoBrief Premium!",
            html_content=html_content,
            text_content=text_content,
        )


# Global email service instance
email_service = EmailService()
