import redis
import os
import threading

host = os.getenv("REDIS_HOST", "localhost")
port = int(os.getenv("REDIS_POST", "6379"))

r = redis.Redis(host=host, port=port, decode_responses=True)

def subscribe(channel):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
       if message['data'] == 'stop_listening':
           break
       print(message['data'])

channel = ''
t = threading.Thread(target=subscribe, args=(channel,))
t.daemon = True
