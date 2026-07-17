# il file contenente le routes API
from fastapi import APIRouter, Body, Response, status, HTTPException
from app.models import User
from app.models import ResponseAPI, ResponseUserAPI, User
from app.storage import read_db, write_db

routes = APIRouter()

@routes.get("/get-user/{email}", response_model=ResponseAPI[ResponseUserAPI[User | None]], 
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
                        "status": 404
                    }
                }
            }
        }
    }            
)
def get_user(email: str):
    db = read_db()
    
    # Cerca l'utente tramite l'id
    for u in db:
        if u["data_user"] is None:
            continue
        
        if u["data_user"]["email"] == email:
            return ResponseAPI[ResponseUserAPI[User | None]](
                success=True,
                message="L'utente è stato trovato",
                data=ResponseUserAPI[User | None](
                    id=u["id"],
                    data_user=u["data_user"]
                ),
                status=200,
            )
            
    # Nessun utente trovato    
    return ResponseAPI[ResponseUserAPI[User | None]](
        success=True,
        message="Valori ritornati",
        data=ResponseUserAPI[None](
            id=u["id"],
            data_user=None
        ),
        status=404
    )

@routes.post(
    "/save-user",
    response_model=ResponseAPI[ResponseUserAPI[User | None]],
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
                        "status": 409
                    }
                }
            }
        }
    }
)
def post_user(user: User, response: Response):

    db = read_db()

    # Cerca l'utente e confrontalo con quello da salvare onde evitare doppioni
    for u_d in db:
        if u_d["data_user"] is None:
            continue
        
        if u_d["data_user"]["email"] == user.email:
            raise HTTPException(
                status_code=409,
                detail="Email già registrata"
            )
            return ResponseAPI[ResponseUserAPI[None]](
                success=False,
                message="Utente già presente nel database",
                data=ResponseUserAPI[None](
                    id=-1,
                    data_user=None    
                ),
                status=409
            )
            
    # Genera un nuovo ID
    new_id = (max([u["id"] for u in db]) + 1)
    
    # Crea il nuovo record come da DB
    new_record = ResponseUserAPI[User](
        id=new_id,
        data_user=user
    )
    
    # Aggiorna il DB
    db.append(new_record.dict())
    write_db(db)        

    # Risposta finale
    response.status_code=status.HTTP_200_OK
    return ResponseAPI[ResponseUserAPI[User]](
        success=True,
        message="Utente salvato correttamente",
        data=new_record,
        status=200
    )

@routes.put(
    "/change-user",
    response_model=ResponseAPI[ResponseUserAPI[User | None]],
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
                        "status": 409
                    }
                }
            }
        }
    }
)
def put_user(
    user: User,
    response: Response,
):
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
            success=False,
            message="Utente non trovato",
            data=None,
            status=404
        )

    # 2. Aggiorna i campi modificati
    updated_user = User(
        name=user.name or target_record["data_user"]["name"],
        lastName=user.lastName or target_record["data_user"]["lastName"],
        address=user.address or target_record["data_user"]["address"],
        prePhone=user.prePhone or target_record["data_user"]["prePhone"],
        phone=user.phone or target_record["data_user"]["phone"],
        email=user.email,  # email è la chiave di ricerca
        pw=user.pw or target_record["data_user"]["pw"]
    )

    # 3. Aggiorna il record nel DB
    target_record["data_user"] = updated_user.dict()

    write_db(db)

    # 4. Risposta finale
    return ResponseAPI[ResponseUserAPI[User]](
        success=True,
        message="Utente aggiornato correttamente",
        data=ResponseUserAPI[User](
            id=target_record["id"],
            data_user=updated_user
        ),
        status=200
    )
    
@routes.delete(
    "/delete-user",
    response_model=ResponseAPI[ResponseUserAPI[User | None]]
)
def delete_user(email: str, response: Response):
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
            data=ResponseUserAPI[None](
                id=target_record["id"],
                data_user=None
            ),
            status=404
        )

    # SOFT DELETE
    target_record["data_user"] = None
    # target_record["deleted_at"] = datetime.now().isoformat()

    write_db(db)

    return ResponseAPI[ResponseUserAPI[None]](
        success=True,
        message="Utente marcato come eliminato",
        data=ResponseUserAPI[None](
            id=target_record["id"],
            data_user=None
        ),
        status=200
    )
