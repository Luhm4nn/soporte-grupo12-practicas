import logging
import os

import redis
from rq import Worker, Queue, Connection

from app.config import settings

logger = logging.getLogger(__name__)

listen = ["default"]

redis_conn = redis.from_url(settings.redis_url)


def run_worker():
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, listen)))
        logger.info("RQ Worker started. Listening on queues: %s", listen)
        worker.work()
