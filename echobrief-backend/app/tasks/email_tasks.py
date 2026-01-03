import logging

from ..core.celery_app import celery_app
from ..services.email_service import email_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="send_password_reset_email")
def send_password_reset_email_task(self, to_email: str, reset_token: str):
    """Send password reset email asynchronously"""
    try:
        logger.info(f"Sending password reset email to {to_email}")
        success = email_service.send_password_reset_email(to_email, reset_token)

        if success:
            logger.info(f"Password reset email sent successfully to {to_email}")
            return {"status": "success", "email": to_email}
        else:
            logger.error(f"Failed to send password reset email to {to_email}")
            return {"status": "failed", "email": to_email}

    except Exception as e:
        logger.error(f"Error sending password reset email to {to_email}: {e}")
        # Retry the task
        raise self.retry(countdown=60, max_retries=3)


@celery_app.task(bind=True, name="send_subscription_success_email")
def send_subscription_success_email_task(
    self,
    to_email: str,
    user_name: str,
    plan_type: str = "paid",
    amount: str | None = None,
):
    """Send subscription success email asynchronously"""
    try:
        logger.info(
            f"Sending subscription success email to {to_email} for user {user_name}"
        )
        success = email_service.send_subscription_success_email(
            to_email, user_name, plan_type, amount
        )

        if success:
            logger.info(f"Subscription success email sent successfully to {to_email}")
            return {"status": "success", "email": to_email, "user_name": user_name}
        else:
            logger.error(f"Failed to send subscription success email to {to_email}")
            return {"status": "failed", "email": to_email, "user_name": user_name}

    except Exception as e:
        logger.error(f"Error sending subscription success email to {to_email}: {e}")
        # Retry the task
        raise self.retry(countdown=60, max_retries=3)
