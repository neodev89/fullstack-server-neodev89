# il file contenente le routes API
from fastapi import APIRouter, Body, Response, status, HTTPException
from datetime import datetime

from app.models import (
    ResponseAPI,
    ResponseUserAPI,
    ReqUser,
    LoginUser,
    ResUser,
    InvoiceSchema,
    PartialUser,
    PartialInvoice,
    PartialInvoiceSchema,
)
from app.factoryFunc import make_response_example
from app.responses_obj import make_partial_invoice_example
from app.responses_obj import make_user_example
from app.storage import read_db, write_db, p_read_db, p_write_db
from app.invoices import Invoice
from app.users import UserRegistered
from app.db import async_session
from sqlalchemy import select
from app.queue import login_queue, block_request, invoice_queue, block_request_invoice
from app.workers.login_worker import process_login_event, heavy_task
from urllib.parse import unquote
from rq import Retry

routes = APIRouter()


@routes.get(
    "/get-user/{email}",
    response_model=ResponseAPI[ResponseUserAPI[ResUser | None]],
    responses={
        404: {
            "description": "Nessun utente trovato",
            "content": {
                "application/json": {
                    "schema": ResponseAPI.schema(),
                    "example": {
                        "success": False,
                        "message": "Nessun utente trovato",
                        "data": None,
                        "status": 404,
                    },
                }
            },
        }
    },
)
async def get_user(email: str):
    try:
        db = read_db()

        # 1. Decodifica %40 in '@', rimuovi spazi bianchi e converti in minuscolo
        cleaned_email = unquote(email).strip().lower()

        # Cerca l'utente tramite l'id
        for u in db:
            if u["data_user"] is None:
                continue

            # Normalizza anche l'email letta dal DB per un confronto sicuro
            db_email = u["data_user"].get("email", "").strip().lower()

            if db_email == cleaned_email:
                return ResponseAPI[ResponseUserAPI[ResUser]](
                    success=True,
                    message="L'utente è stato trovato",
                    data=ResponseUserAPI[ResUser](id=u["id"], data_user=u["data_user"]),
                    status=200,
                )

        # Nessun utente trovato
        return ResponseAPI[ResponseUserAPI[None]](
            success=False,
            message=f"Valori non ritornati perché {email} ha un valore non corretto",
            data=ResponseUserAPI[None](id=u["id"], data_user=None),
            status=404,
        )

    except Exception as e:
        # Log utile per debugging
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )


@routes.get(
    "/get-invoice-user/{token}", response_model=ResponseAPI[list[InvoiceSchema]]
)
async def get_invoice_user(token: str):
    try:
        async with async_session() as session:
            stmt = select(Invoice).where(Invoice.invoice_token == token)
            result = await session.execute(stmt)
            invoices = result.scalars().all()

            if invoices:
                return ResponseAPI[list[InvoiceSchema]](
                    success=True, message="Dati ottenuti", data=invoices, status=200
                )

            return ResponseAPI[None](
                success=False,
                message=f"Nessuna fattura trovata per il token {token}",
                data=None,
                status=404,
            )

    except Exception as e:
        # Log utile per debugging
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )


@routes.get(
    "/get-invoice-to-user/{token}",
    response_model=ResponseAPI[PartialInvoiceSchema | None],
    responses={
        **make_response_example(
            status=200,
            message="Fatture e dati utente ottenuti!",
            data_example=make_partial_invoice_example(),
            success=True,
        ),
        **make_response_example(
            status=400,
            message="Fatture e dati utente non ottenuti!",
            data_example=None,
            success=False,
        ),
        **make_response_example(
            status=500,
            message="Chiamata API fallita!",
            data_example=None,
            success=False,
        ),
    },
)
async def get_invoice_to_user_joined(token: str):
    try:
        print("invocata api")

        async with async_session() as session:
            stmt = (
                select(Invoice, UserRegistered)
                .join(UserRegistered, Invoice.invoice_token == UserRegistered.id)
                .where(UserRegistered.id == token)
            )

            result = await session.execute(stmt)
            row = result.one_or_none()

            if row is None:
                return ResponseAPI[None](
                    success=False,
                    message="Nessun dato trovato per questo token",
                    data=None,
                    status=400,
                )
            
            print(f"i dat6i recuperati sono: {row}")

            invoice, user = row

            joinedInvUser = PartialInvoiceSchema(
                id=invoice.id,
                created_at=invoice.created_at,
                num_invoice=invoice.num_invoice,
                taxable=invoice.taxable,
                vat=invoice.vat,
                total=invoice.total,
                creation_date=invoice.creation_date,
                protocol_numb=invoice.protocol_numb,
                tax_id_code=invoice.tax_id_code,
                name=user.name,
                lastName=user.lastName,
                email=user.email,
            )


            return ResponseAPI[PartialInvoiceSchema](
                success=True,
                message="utente e fatture unite e ritornate",
                data=joinedInvUser,
                status=200,
            )

    except Exception as e:
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )


@routes.post(
    "/save-user",
    response_model=ResponseAPI[ResponseUserAPI[ResUser | None]],
    responses={
        **make_response_example(
            status=409,
            message="Email già registrata!",
            data_example=None,
            success=False,
        ),
        **make_response_example(
            status=404, message="Email non trovata", data_example=None, success=False
        ),
        **make_response_example(
            status=200,
            message="utente registrato con successo",
            data_example=make_user_example,
            success=True,
        ),
    },
)
async def post_user(user: ReqUser, response: Response):
    try:

        db = read_db()

        # Cerca l'utente e confrontalo con quello da salvare onde evitare doppioni
        for u_d in db:
            if u_d["data_user"] is None:
                continue

            if u_d["data_user"]["email"] == user.email:
                return ResponseAPI[ResponseUserAPI[None]](
                    success=False,
                    message="Utente già presente nel database",
                    data=ResponseUserAPI[None](id=-1, data_user=None),
                    status=409,
                )

        # Genera un nuovo ID
        new_id = max([u["id"] for u in db]) + 1
        new_tk = ""
        if new_id == 0:
            new_tk = "iduserfittizio"

        new_tk = f"iduserfittizio_{new_id}"

        new_user = {
            "name": user.name,
            "lastName": user.lastName,
            "address": user.address,
            "prePhone": user.prePhone,
            "phone": user.phone,
            "email": user.email,
            "pw": user.pw,
            "tk": new_tk,
        }

        # Crea il nuovo record come da DB
        new_record = ResponseUserAPI[ResUser](id=new_id, data_user=new_user)

        # Aggiorna il DB
        db.append(new_record.dict())
        write_db(db)

        # Risposta finale
        response.status_code = status.HTTP_200_OK
        return ResponseAPI[ResponseUserAPI[ResUser]](
            success=True,
            message="Utente salvato correttamente",
            data=new_record,
            status=200,
        )
    except Exception as e:
        # Log utile per debugging
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )


@routes.post(
    "/login-user",
    response_model=ResponseAPI[ResponseUserAPI[ResUser | None]],
)
async def post_login_user(user: LoginUser, response: Response):
    try:
        db = read_db()

        # Cerca l'utente e confrontalo con quello da salvare onde evitare doppioni
        for u_d in db:
            if u_d["data_user"] is None:
                continue

            if u_d["data_user"]["email"] == user.email:
                response.status_code = status.HTTP_200_OK
                # 🔥 QUEUE: push del job
                job = login_queue.enqueue(
                    process_login_event,
                    user.email,
                    retry=Retry(max=5, interval=[3, 9, 21]),
                    job_timeout=31,
                )
                job1 = block_request.enqueue(
                    heavy_task,
                    job_timeout=30,
                )
                return ResponseAPI[ResponseUserAPI[ResUser]](
                    success=True,
                    message="Utente loggato correttamente",
                    data=ResponseUserAPI[ResUser](
                        id=u_d["id"],
                        data_user={**u_d["data_user"], "tk": u_d["data_user"]["tk"]},
                    ),
                    status=200,
                )

        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseAPI[ResponseUserAPI[None]](
            success=False,
            message="Utente non trovato",
            data=ResponseUserAPI[None](
                id=-1,
                data_user=None,
            ),
            status=404,
        )
    except Exception as e:
        # Log utile per debugging
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )


@routes.put(
    "/change-user",
    response_model=ResponseAPI[ResponseUserAPI[ResUser | None]],
    responses={
        409: {
            "description": "Email già registrata",
            "content": {
                "application/json": {
                    "schema": ResponseAPI.schema(),
                    "example": {
                        "success": False,
                        "message": "Email già registrata",
                        "data": None,
                        "status": 409,
                    },
                }
            },
        }
    },
)
async def put_user(
    user: ReqUser,
    response: Response,
):
    try:
        db = read_db()

        # 1. Cerca il record da modificare
        target_record = None
        for record in db:
            data_user = record.get("data_user")

            if data_user is None:
                continue

            # match per email (identifica l'utente)
            if data_user["email"] == user.email:
                target_record = record
                break

        if not target_record:
            return ResponseAPI[ResponseUserAPI[None]](
                success=False, message="Utente non trovato", data=None, status=404
            )

        # 2. Aggiorna i campi modificati
        updated_user = ReqUser(
            name=user.name or target_record["data_user"]["name"],
            lastName=user.lastName or target_record["data_user"]["lastName"],
            address=user.address or target_record["data_user"]["address"],
            prePhone=user.prePhone or target_record["data_user"]["prePhone"],
            phone=user.phone or target_record["data_user"]["phone"],
            email=user.email,  # email è la chiave di ricerca
            pw=user.pw or target_record["data_user"]["pw"],
        )

        # 3. Aggiorna il record nel DB
        target_record["data_user"] = updated_user.dict()

        write_db(db)

        # 4. Risposta finale
        return ResponseAPI[ResponseUserAPI[ResUser]](
            success=True,
            message="Utente aggiornato correttamente",
            data=ResponseUserAPI[ResUser](
                id=target_record["id"], data_user=updated_user
            ),
            status=200,
        )

    except Exception as e:
        # Log utile per debugging
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )


@routes.delete(
    "/delete-user", response_model=ResponseAPI[ResponseUserAPI[ResUser | None]]
)
async def delete_user(email: str, response: Response):
    try:
        db = read_db()

        target_record = None

        for record in db:
            data_user = record.get("data_user")

            if data_user is None:
                continue

            if data_user["email"] == email:
                target_record = record
                break

        if not target_record:
            return ResponseAPI[ResponseUserAPI[None]](
                success=False,
                message="Utente non trovato",
                data=ResponseUserAPI[None](id=target_record["id"], data_user=None),
                status=404,
            )

        # SOFT DELETE
        target_record["data_user"] = None
        # target_record["deleted_at"] = datetime.now().isoformat()

        write_db(db)

        return ResponseAPI[ResponseUserAPI[None]](
            success=True,
            message="Utente marcato come eliminato",
            data=ResponseUserAPI[None](id=target_record["id"], data_user=None),
            status=200,
        )
    except Exception as e:
        # Log utile per debugging
        print(f"[API ERROR] get_invoice_user: {e}")

        return ResponseAPI[None](
            success=False,
            message="Errore interno durante il recupero delle fatture",
            data=None,
            status=500,
        )
