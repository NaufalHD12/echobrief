#!/usr/bin/env python3
"""
Script to run and test email tasks with Celery.
Supports testing password reset and subscription success emails.

Usage:
    # Test password reset email
    python scripts/run_email_tasks.py --password-reset --email user@example.com

    # Test subscription success email
    python scripts/run_email_tasks.py --subscription-success --email user@example.com --username johndoe --amount 5.00

    # Run worker only
    python scripts/run_email_tasks.py --worker-only

    # Check status
    python scripts/run_email_tasks.py --check-status
"""

import os
import sys
import time
import subprocess
import argparse
import logging
from typing import Optional

# Add project root to Python path for proper module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.tasks.email_tasks import send_password_reset_email_task, send_subscription_success_email_task  # noqa: E402
from app.core.celery_app import celery_app  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailTaskRunner:
    def __init__(self):
        self.worker_process: Optional[subprocess.Popen] = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)

    def run_worker(self) -> subprocess.Popen:
        """Run Celery worker with Windows-compatible settings"""
        logger.info("Starting Celery worker for email tasks...")

        # Change to project root directory
        os.chdir(self.project_root)

        # Command for Windows-compatible worker
        worker_cmd = [
            sys.executable, "-m", "celery",
            "-A", "app.core.celery_app",
            "worker",
            "--pool=solo",  # Windows-compatible pool
            "--loglevel=info",
            "--concurrency=1",  # Single worker for simplicity
            "--queues=email"  # Specific queue for email tasks
        ]

        logger.info(f"Worker command: {' '.join(worker_cmd)}")
        process = subprocess.Popen(worker_cmd)
        logger.info(f"Celery worker started with PID: {process.pid}")
        return process

    def test_password_reset_email(self, email: str) -> dict:
        """Test password reset email task"""
        logger.info(f"Testing password reset email for: {email}")

        try:
            # Generate a test reset token (in real scenario this would come from auth service)
            test_token = "test-reset-token-12345"

            result = send_password_reset_email_task.delay(email, test_token)
            logger.info(f"Password reset email task submitted. Task ID: {result.id}")

            # Wait for result with timeout
            result_data = result.get(timeout=30)  # 30 second timeout
            logger.info(f"Password reset email task completed: {result_data}")
            return result_data
        except Exception as e:
            logger.error(f"Error testing password reset email: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def test_subscription_success_email(self, email: str, username: str, amount: Optional[str] = None) -> dict:
        """Test subscription success email task"""
        logger.info(f"Testing subscription success email for: {email} ({username})")

        try:
            result = send_subscription_success_email_task.delay(email, username, "paid", amount)
            logger.info(f"Subscription success email task submitted. Task ID: {result.id}")

            # Wait for result with timeout
            result_data = result.get(timeout=30)  # 30 second timeout
            logger.info(f"Subscription success email task completed: {result_data}")
            return result_data
        except Exception as e:
            logger.error(f"Error testing subscription success email: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def check_celery_status(self) -> bool:
        """Check if Celery is properly connected and running"""
        logger.info("Checking Celery status...")

        try:
            # Check Celery connection
            inspection = celery_app.control.inspect()
            active_workers = inspection.active()
            logger.info(f"Active Celery workers: {active_workers}")

            # Check scheduled tasks
            scheduled = inspection.scheduled()
            logger.info(f"Scheduled tasks: {scheduled}")

            # Check registered tasks
            registered = inspection.registered()
            logger.info(f"Registered tasks: {registered}")

            # Check if email tasks are registered
            if registered:
                email_tasks_found = []
                for worker_tasks in registered.values():
                    if worker_tasks:
                        for task in worker_tasks:
                            if 'email' in task.lower():
                                email_tasks_found.append(task)

                if email_tasks_found:
                    logger.info(f"Email tasks found: {email_tasks_found}")
                else:
                    logger.warning("No email tasks found in registered tasks")

            return True
        except Exception as e:
            logger.error(f"Celery status check failed: {e}")
            return False

    def cleanup(self):
        """Clean up any running processes"""
        if self.worker_process:
            logger.info(f"Terminating worker process (PID: {self.worker_process.pid})")
            self.worker_process.terminate()
            self.worker_process.wait()
            self.worker_process = None

def main():
    parser = argparse.ArgumentParser(
        description='Run and test email tasks with Celery',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Add arguments
    parser.add_argument('--password-reset', action='store_true',
                       help='Test password reset email')
    parser.add_argument('--subscription-success', action='store_true',
                       help='Test subscription success email')
    parser.add_argument('--email', type=str, required=False,
                       help='Email address for testing')
    parser.add_argument('--username', type=str, default='TestUser',
                       help='Username for subscription email (default: TestUser)')
    parser.add_argument('--amount', type=str, default='5.00',
                       help='Amount for subscription email (default: 5.00)')
    parser.add_argument('--worker-only', action='store_true',
                       help='Run worker only')
    parser.add_argument('--check-status', action='store_true',
                       help='Check Celery status')

    args = parser.parse_args()

    runner = EmailTaskRunner()

    try:
        if args.check_status:
            # Check Celery status
            status_ok = runner.check_celery_status()
            sys.exit(0 if status_ok else 1)

        elif args.password_reset:
            if not args.email:
                print("❌ Error: --email is required for password reset test")
                sys.exit(1)

            # Test password reset email
            result = runner.test_password_reset_email(args.email)

            if result.get("status") == "success":
                print("✅ Password reset email sent successfully!")
                print(f"   Email: {result.get('email')}")
            else:
                print(f"❌ Password reset email failed: {result.get('error')}")
                sys.exit(1)

        elif args.subscription_success:
            if not args.email:
                print("❌ Error: --email is required for subscription success test")
                sys.exit(1)

            # Test subscription success email
            result = runner.test_subscription_success_email(args.email, args.username, args.amount)

            if result.get("status") == "success":
                print("✅ Subscription success email sent successfully!")
                print(f"   Email: {result.get('email')}")
                print(f"   Username: {result.get('user_name')}")
            else:
                print(f"❌ Subscription success email failed: {result.get('error')}")
                sys.exit(1)

        elif args.worker_only:
            # Run worker only
            runner.worker_process = runner.run_worker()

            logger.info("Celery worker is running for email tasks. Press Ctrl+C to stop.")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\nShutting down worker...")
                runner.cleanup()
                logger.info("Worker stopped.")

        else:
            # No arguments provided, show help
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        runner.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
