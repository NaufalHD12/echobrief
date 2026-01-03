#!/usr/bin/env python3
"""
Script to run subscription management tasks with Celery.
Supports checking expired subscriptions and cleaning up old data.

Usage:
    # Check expired subscriptions
    python scripts/run_subscription_management.py --check-expired

    # Clean up old subscriptions
    python scripts/run_subscription_management.py --cleanup-old

    # Run worker only
    python scripts/run_subscription_management.py --worker-only

    # Check status
    python scripts/run_subscription_management.py --check-status
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

from app.tasks.subscription_management import check_expired_subscriptions_task, cleanup_old_subscriptions_task  # noqa: E402
from app.core.celery_app import celery_app  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubscriptionManagementRunner:
    def __init__(self):
        self.worker_process: Optional[subprocess.Popen] = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)

    def run_worker(self) -> subprocess.Popen:
        """Run Celery worker with Windows-compatible settings"""
        logger.info("Starting Celery worker for subscription management tasks...")

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
            "--queues=subscription_management"  # Specific queue for subscription tasks
        ]

        logger.info(f"Worker command: {' '.join(worker_cmd)}")
        process = subprocess.Popen(worker_cmd)
        logger.info(f"Celery worker started with PID: {process.pid}")
        return process

    def run_check_expired_subscriptions(self) -> dict:
        """Run check expired subscriptions task"""
        logger.info("Running check expired subscriptions task...")

        try:
            result = check_expired_subscriptions_task.delay()
            logger.info(f"Check expired subscriptions task submitted. Task ID: {result.id}")

            # Wait for result with timeout
            result_data = result.get(timeout=60)  # 1 minute timeout
            logger.info(f"Check expired subscriptions task completed: {result_data}")
            return {"success": True, "expired_count": result_data}
        except Exception as e:
            logger.error(f"Error running check expired subscriptions task: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def run_cleanup_old_subscriptions(self) -> dict:
        """Run cleanup old subscriptions task"""
        logger.info("Running cleanup old subscriptions task...")

        try:
            result = cleanup_old_subscriptions_task.delay()
            logger.info(f"Cleanup old subscriptions task submitted. Task ID: {result.id}")

            # Wait for result with timeout
            result_data = result.get(timeout=60)  # 1 minute timeout
            logger.info(f"Cleanup old subscriptions task completed: {result_data}")
            return {"success": True, "cleaned_count": result_data}
        except Exception as e:
            logger.error(f"Error running cleanup old subscriptions task: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

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

            # Check if subscription management tasks are registered
            if registered:
                subscription_tasks_found = []
                for worker_tasks in registered.values():
                    if worker_tasks:
                        for task in worker_tasks:
                            if 'subscription' in task.lower():
                                subscription_tasks_found.append(task)

                if subscription_tasks_found:
                    logger.info(f"Subscription management tasks found: {subscription_tasks_found}")
                else:
                    logger.warning("No subscription management tasks found in registered tasks")

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
        description='Run subscription management tasks with Celery',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Add arguments
    parser.add_argument('--check-expired', action='store_true',
                       help='Check and update expired subscriptions')
    parser.add_argument('--cleanup-old', action='store_true',
                       help='Clean up old expired subscriptions (>6 months)')
    parser.add_argument('--worker-only', action='store_true',
                       help='Run worker only')
    parser.add_argument('--check-status', action='store_true',
                       help='Check Celery status')

    args = parser.parse_args()

    runner = SubscriptionManagementRunner()

    try:
        if args.check_status:
            # Check Celery status
            status_ok = runner.check_celery_status()
            sys.exit(0 if status_ok else 1)

        elif args.check_expired:
            # Run check expired subscriptions
            result = runner.run_check_expired_subscriptions()

            if result.get("success"):
                print("✅ Check expired subscriptions completed successfully!")
                print(f"   Subscriptions expired: {result.get('expired_count')}")
            else:
                print(f"❌ Check expired subscriptions failed: {result.get('error')}")
                sys.exit(1)

        elif args.cleanup_old:
            # Run cleanup old subscriptions
            result = runner.run_cleanup_old_subscriptions()

            if result.get("success"):
                print("✅ Cleanup old subscriptions completed successfully!")
                print(f"   Subscriptions cleaned up: {result.get('cleaned_count')}")
            else:
                print(f"❌ Cleanup old subscriptions failed: {result.get('error')}")
                sys.exit(1)

        elif args.worker_only:
            # Run worker only
            runner.worker_process = runner.run_worker()

            logger.info("Celery worker is running for subscription management tasks. Press Ctrl+C to stop.")

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
