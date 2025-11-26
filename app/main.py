from fastapi import FastAPI
from app.database import engine, Base
from app.auth_routes import router as auth_router
from app.routes import router as books_router
from . import models, auth
from . import auth_routes
from app.auth_admin import router as admin_router
from app.routes_all_user import router as admin_operations_router


import os
from dotenv import load_dotenv


load_dotenv()
# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])


app.include_router(admin_router)
app.include_router(admin_operations_router)
app.include_router(auth_router)
app.include_router(books_router)


@app.get("/")
def home():
    return {"message": "Book API"}
