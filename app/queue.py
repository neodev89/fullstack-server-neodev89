from redis import Redis
from rq import Queue


redis_conn = Redis(host="localhost", port=6379)
login_queue = Queue("login_queue", connection=redis_conn)
