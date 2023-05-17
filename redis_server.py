import redis
import os

host = os.getenv("REDIS_HOST", "localhost")
port = int(os.getenv("REDIS_POST", "6379"))

R = redis.Redis(host=host, port=port, decode_responses=True)

def create_redis_lock(id):
    return R.lock(id)