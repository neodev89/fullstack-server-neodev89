from app.models import ResponseAPI

def make_response_example(
    status: int,
    message: str,
    data_example: dict | None,
    success: bool | None = None,
):
    if success is None:
        success = status < 400

    return {
        status: {
            "description": message,
            "content": {
                "application/json": {
                    "schema": ResponseAPI.schema(),
                    "example": {
                        "success": success,
                        "message": message,
                        "data": data_example,
                        "status": status,
                    },
                }
            },
        }
    }
