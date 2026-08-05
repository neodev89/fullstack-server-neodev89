from redis import Redis
from rq import Queue, Worker

def process_login_event(email: str):
    print(f"[WORKER] Elaboro login per {email}")
    return {"status": "ok", "email": email}

if __name__ == "__main__":
    # Connessione Redis
    redis_conn = Redis(host="localhost", port=6379)

    # Queue moderna: si passa la connessione direttamente
    queue = Queue("login_queue", connection=redis_conn)

    # Worker moderno: stessa cosa
    worker = Worker([queue], connection=redis_conn)

    # Avvia il worker
    worker.work()
