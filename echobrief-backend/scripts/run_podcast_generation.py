#!/usr/bin/env python3
"""
Comprehensive script to run podcast generation with Celery.
Supports multiple modes for development, testing, and production.

Usage:
    # Mode 1: Worker + Task sekaligus (untuk testing)
    python scripts/run_podcast_generation.py --worker-and-task

    # Mode 2: Worker saja (untuk scheduled tasks)
    python scripts/run_podcast_generation.py --worker-only

    # Mode 3: Task langsung (tanpa worker)
    python scripts/run_podcast_generation.py --direct-task

    # Mode 4: Generate podcast untuk user tertentu
    python scripts/run_podcast_generation.py --user-id <user_uuid>

    # Mode 5: Check status
    python scripts/run_podcast_generation.py --check-status

    # Mode 6: Run daily podcast generation (3 AM task)
    python scripts/run_podcast_generation.py --daily-task
"""

import os
import sys
import time
import subprocess
import argparse
import logging
import asyncio
from typing import Optional
from uuid import UUID

# Add project root to Python path for proper module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.tasks.podcast_generation import generate_daily_podcasts, generate_podcast_for_user  # noqa: E402
from app.core.celery_app import celery_app  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CeleryRunner:
    def __init__(self):
        self.worker_process: Optional[subprocess.Popen] = None
        self.beat_process: Optional[subprocess.Popen] = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)

    def run_worker(self) -> subprocess.Popen:
        """Run Celery worker with Windows-compatible settings"""
        logger.info("Starting Celery worker for podcast generation...")

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
            "--queues=podcast_generation"  # Specific queue for podcast tasks
        ]

        logger.info(f"Worker command: {' '.join(worker_cmd)}")
        process = subprocess.Popen(worker_cmd)
        logger.info(f"Celery worker started with PID: {process.pid}")
        return process

    def run_daily_task(self) -> dict:
        """Run daily podcast generation task directly without worker"""
        logger.info("Running daily podcast generation task directly...")

        try:
            result = generate_daily_podcasts.delay()
            logger.info(f"Daily task submitted. Task ID: {result.id}")

            # Wait for result with timeout
            result_data = result.get(timeout=1800)  # 30 minute timeout for all users
            logger.info(f"Daily task completed successfully: {result_data}")
            return result_data
        except Exception as e:
            logger.error(f"Error running daily task: {e}", exc_info=True)
            raise

    def run_user_task(self, user_id: str) -> dict:
        """Run podcast generation for specific user"""
        logger.info(f"Running podcast generation for user: {user_id}")

        try:
            # Validate UUID format
            try:
                UUID(user_id)
            except ValueError:
                return {"success": False, "error": "Invalid UUID format"}

            # Run async function directly
            result = asyncio.run(generate_podcast_for_user(user_id))
            logger.info(f"User task completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error running user task: {e}", exc_info=True)
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
        description='Run podcast generation with Celery',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Add arguments
    parser.add_argument('--worker-and-task', action='store_true',
                       help='Run worker and execute daily task immediately')
    parser.add_argument('--worker-only', action='store_true',
                       help='Run worker only (for scheduled tasks)')
    parser.add_argument('--direct-task', action='store_true',
                       help='Run daily task directly without worker')
    parser.add_argument('--daily-task', action='store_true',
                       help='Run daily podcast generation task (3 AM equivalent)')
    parser.add_argument('--user-id', type=str,
                       help='Generate podcast for specific user (UUID format)')
    parser.add_argument('--check-status', action='store_true',
                       help='Check Celery status')

    args = parser.parse_args()

    runner = CeleryRunner()

    try:
        if args.check_status:
            # Check Celery status
            status_ok = runner.check_celery_status()
            sys.exit(0 if status_ok else 1)

        elif args.user_id:
            # Generate podcast for specific user
            result = runner.run_user_task(args.user_id)
            
            if result.get("success"):
                print("\nPodcast generation completed successfully!")
                print(f"User ID: {result.get('user_id')}")
                print(f"Podcast ID: {result.get('podcast_id')}")
                print(f"Topics count: {result.get('topics_count')}")
                print(f"Plan type: {result.get('plan_type')}")
            else:
                print(f"\nPodcast generation failed: {result.get('error')}")
                sys.exit(1)

        elif args.direct_task or args.daily_task:
            # Run daily task directly
            result = runner.run_daily_task()
            
            print("\nDaily podcast generation completed successfully!")
            print(f"Total users: {result['total_users']}")
            print(f"Successful generations: {result['successful_generations']}")
            print(f"Failed generations: {result['failed_generations']}")
            print(f"Skipped users: {result['skipped_users']}")
            
            # Show some details
            if result['details']:
                print("\nFirst 5 results:")
                for detail in result['details'][:5]:
                    print(f"  User {detail['user_id']}: {detail['status']}")

        elif args.worker_only:
            # Run worker only
            runner.worker_process = runner.run_worker()

            logger.info("Celery worker is running. Press Ctrl+C to stop.")
            logger.info("The worker will automatically execute scheduled tasks daily at 3 AM.")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\nShutting down worker...")
                runner.cleanup()
                logger.info("Worker stopped.")

        elif args.worker_and_task:
            # Run worker and execute task
            runner.worker_process = runner.run_worker()

            # Give worker time to start
            time.sleep(3)

            # Run daily task
            result = runner.run_daily_task()

            # Clean up
            runner.cleanup()

            print("\nDaily podcast generation completed successfully!")
            print(f"Total users: {result['total_users']}")
            print(f"Successful generations: {result['successful_generations']}")
            print(f"Failed generations: {result['failed_generations']}")
            print(f"Skipped users: {result['skipped_users']}")

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
