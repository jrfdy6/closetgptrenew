"""Run with python -m src.worker.gamification_runner from backend root."""
import logging
import signal
import time
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from firebase_admin import storage
from ..config.firebase import db
from ..services.wear_projection import process_pending
from ..services.app_data_privacy import process_deletion_jobs
from .gamification_tasks import maintenance_pass

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    if db is None:
        raise RuntimeError("Firebase unavailable; refusing to run gamification worker")
    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    worker_id = "gamification-" + str(uuid4())
    bucket = storage.bucket()
    # Maintenance is isolated so one large account cannot block wear delivery.
    with ThreadPoolExecutor(max_workers=1) as executor:
        maintenance = None
        next_maintenance = 0
        while running:
            try:
                process_pending(db, worker_id, limit=10)
                process_deletion_jobs(db, bucket, limit=2, max_records=100)
                if time.monotonic() >= next_maintenance and (maintenance is None or maintenance.done()):
                    if maintenance is not None:
                        maintenance.result()
                    maintenance = executor.submit(maintenance_pass, db, worker_id)
                    next_maintenance = time.monotonic() + 60
            except Exception:
                logger.exception("Gamification worker pass failed; durable jobs remain retryable")
                if maintenance is not None and maintenance.done():
                    maintenance = None
            time.sleep(5)


if __name__ == "__main__":
    main()
