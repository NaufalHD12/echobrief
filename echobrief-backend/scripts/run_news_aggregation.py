#!/usr/bin/env python3
"""
Comprehensive script to run news aggregation with Celery.
Supports multiple modes for development, testing, and production.

Usage:
    # Mode 1: Worker + Task sekaligus (untuk testing)
    python scripts/run_news_aggregation.py --worker-and-task

    # Mode 2: Worker saja (untuk scheduled tasks)
    python scripts/run_news_aggregation.py --worker-only

    # Mode 3: Task langsung (tanpa worker)
    python scripts/run_news_aggregation.py --direct-task

    # Mode 4: Check status
    python scripts/run_news_aggregation.py --check-status
"""

import os
import sys
import time
import subprocess
import argparse
import logging

# Add project root to Python path for proper module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.tasks.news_aggregation import aggregate_news_task  # noqa: E402
from app.core.celery_app import celery_app  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CeleryRunner:
    def __init__(self):
        self.worker_process = None
        self.beat_process = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)

    def run_worker(self) -> subprocess.Popen:
        """Run Celery worker with Windows-compatible settings"""
        logger.info("Starting Celery worker...")

        # Change to project root directory
        os.chdir(self.project_root)

        # Command for Windows-compatible worker
        worker_cmd = [
            sys.executable, "-m", "celery",
            "-A", "app.core.celery_app",
            "worker",
            "--pool=solo",  # Windows-compatible pool
            "--loglevel=info",
            "--concurrency=1"  # Single worker for simplicity
        ]

        logger.info(f"Worker command: {' '.join(worker_cmd)}")
        process = subprocess.Popen(worker_cmd)
        logger.info(f"Celery worker started with PID: {process.pid}")
        return process

    def run_direct_task(self) -> dict:
        """Run news aggregation task directly without worker"""
        logger.info("Running news aggregation task directly...")

        try:
            result = aggregate_news_task.delay()
            logger.info(f"Task submitted. Task ID: {result.id}")

            # Wait for result with timeout
            result_data = result.get(timeout=600)  # 5 minute timeout
            logger.info(f"Task completed successfully: {result_data}")
            return result_data
        except Exception as e:
            logger.error(f"Error running direct task: {e}", exc_info=True)
            raise

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

        if self.beat_process:
            logger.info(f"Terminating beat process (PID: {self.beat_process.pid})")
            self.beat_process.terminate()
            self.beat_process.wait()
            self.beat_process = None

def main():
    parser = argparse.ArgumentParser(
        description='Run news aggregation with Celery',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Add arguments
    parser.add_argument('--worker-and-task', action='store_true',
                       help='Run worker and execute task immediately')
    parser.add_argument('--worker-only', action='store_true',
                       help='Run worker only (for scheduled tasks)')
    parser.add_argument('--direct-task', action='store_true',
                       help='Run task directly without worker')
    parser.add_argument('--check-status', action='store_true',
                       help='Check Celery status')

    args = parser.parse_args()

    runner = CeleryRunner()

    try:
        if args.check_status:
            # Check Celery status
            status_ok = runner.check_celery_status()
            sys.exit(0 if status_ok else 1)

        elif args.direct_task:
            # Run task directly
            result = runner.run_direct_task()
            print("\nNews aggregation completed successfully!")
            print(f"Total processed: {result['total_processed']}")
            print(f"New articles: {result['total_new_articles']}")

        elif args.worker_only:
            # Run worker only
            runner.run_worker()

            logger.info("Celery worker is running. Press Ctrl+C to stop.")
            logger.info("The worker will automatically execute scheduled tasks every 6 hours.")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\nShutting down worker...")
                runner.cleanup()
                logger.info("Worker stopped.")

        elif args.worker_and_task:
            # Run worker and execute task
            runner.run_worker()

            # Give worker time to start
            time.sleep(3)

            # Run task
            result = runner.run_direct_task()

            # Clean up
            runner.cleanup()

            print("\nNews aggregation completed successfully!")
            print(f"Total processed: {result['total_processed']}")
            print(f"New articles: {result['total_new_articles']}")

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
