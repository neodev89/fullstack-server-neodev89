from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ✔️ aggiunto
    allow_headers=["*"],
)


app.include_router(routes, prefix="/api")