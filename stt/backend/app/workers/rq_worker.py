import logging
import os

import redis
from rq import Worker, Queue

from app.config import settings

logger = logging.getLogger(__name__)

listen = ["default"]

redis_conn = redis.from_url(settings.redis_url)


def run_worker():
    queues = [Queue(name, connection=redis_conn) for name in listen]
    worker = Worker(queues, connection=redis_conn)
    logger.info("RQ Worker started. Listening on queues: %s", listen)
    worker.work()


if __name__ == "__main__":
    run_worker()
