from fastapi import FastAPI
from app.api.v1 import users

app = FastAPI(
    title="FastAPI Shop",
    version="0.1.0",
)

app.include_router(users.router, prefix='/api/v1/users', tags=['Users'])

@app.get("/health")
def health_check():
    return {"status": "ok"}
