from redis import Redis
from app.infrastructure.settings import settings
def get_redis_connection():
    if settings.REDIS_PASSWORD:
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD
        )
    else:
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )

redis_client = get_redis_connection()