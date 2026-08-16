from redis import Redis
from rq import Queue, Worker


async def process_invoice_event(invoice_token: str):
    print(f"[WORKER] Elaboro le fatture per token: {invoice_token}")

    try:
        # 1) Validazione token
        if not validate_token(invoice_token):
            return {"status": "error", "reason": "invalid_token"}

        # 2) Query DB
        invoices = fetch_invoices_by_token(invoice_token)

        # 3) Serializzazione
        serialized = [inv.to_dict() for inv in invoices]

        # 4) Logging
        print(f"[WORKER] Fatture trovate: {len(serialized)}")

        # 5) Risposta
        return {"status": "ok", "count": len(serialized), "invoices": serialized}

    except Exception as e:
        print(f"[WORKER] Errore: {e}")
        return {"status": "error", "reason": str(e)}


if __name__ == "__main__":
    # Connessione Redis
    redis_conn = Redis(host="localhost", port="6380")

    # Queue moderna: si passa la connessione diretta
    queue = Queue("invoice_queue", connection=redis_conn)
    block_req = Queue("block_request_invoice", connection=redis_conn)

    # Worker moderno: si passa la connessione diretta
    worker = Worker([queue, block_req], connection=redis_conn)

    # Avvia il worker
    worker.work()
