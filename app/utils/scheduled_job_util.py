import traceback
from typing import Callable

import redis_lock

from app.infrastructure.redis import redis_client
from app.utils.logging_util import log_message, LogLevel


def distributed_job(job: Callable, job_name: str):
    lock = None
    try:
        lock = redis_lock.Lock(redis_client, name=job_name, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            log_message(LogLevel.INFO, f"Starting scheduled {job_name}...")
            job()
            log_message(LogLevel.INFO, f"Successfully completed scheduled {job_name}")
            lock.release()
        else:
            log_message(LogLevel.INFO, f"{job_name} running on another instance")
    except Exception as e:
        if lock is not None:
            lock.release()
        log_message(LogLevel.ERROR, f"Error in scheduled {job_name}", error=str(e))