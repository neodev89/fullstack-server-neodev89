from redis import Redis
from rq import Queue


redis_conn = Redis(host="localhost", port=6379)
login_queue = Queue("login_queue", connection=redis_conn)
block_request = Queue("block_request", connection=redis_conn)
invoice_queue = Queue("invoice_queue", connection=redis_conn)
block_request_invoice = Queue("block_request_invoice", connection=redis_conn)