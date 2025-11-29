from fastapi import FastAPI
from app.api.v1 import users, auth, categories, products

app = FastAPI(
    title="FastAPI Shop",
    version="0.1.0",
)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['Auth'])
app.include_router(users.router, prefix='/api/v1/users', tags=['Users'])
app.include_router(categories.router, prefix='/api/v1/categories', tags=['Categories'])
app.include_router(products.router, prefix='/api/v1/products', tags=['Products'])

@app.get("/health")
def health_check():
    return {"status": "ok"}
