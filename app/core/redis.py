import redis
from redis.exceptions import ConnectionError,TimeoutError
from .config import settings

r = redis.Redis(
    host="localhost",
    port=6370,
    db=0
)

