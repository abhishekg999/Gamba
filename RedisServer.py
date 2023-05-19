import redis
import os
import sys
import datetime

host = os.getenv("REDIS_HOST", "localhost")
port = int(os.getenv("REDIS_POST", "6379"))


R = redis.Redis(host=host, port=port, decode_responses=True)

try:
    R.set("meta:time_start", str(datetime.datetime.now()))
    print("Connected to Redis server!")
except:
    print("Unable to connect to Redis server.")
    sys.exit(1)


def create_redis_lock(id):
    return R.lock(id)

 