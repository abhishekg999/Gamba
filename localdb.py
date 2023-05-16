import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

for key in r.scan_iter():
       print(key)
