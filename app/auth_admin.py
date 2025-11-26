from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, crud
from app.auth import ALGORITHM, SECRET_KEY, admin_required, create_access_token, create_reset_token, verify_reset_token
from app.email_utils import send_email
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from werkzeug.security import check_password_hash
from app.auth import SECRET_KEY, ALGORITHM
from app.auth import create_access_token


router = APIRouter(prefix="/admin" , tags=["Admin"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard")
def admin_dashboard(token: str = Depends(admin_required)):
    return {"message": "Welcome Admin!"}



@router.post("/create")
def create_admin(admin:schemas.AdminCreate ,db:Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, admin.username)
    if existing:
         raise HTTPException(status_code=400 , detail="Admin username already exists")
    crud.create_admin(db, admin)
    return {"message":"Admin created successfully"}
 

@router.post("/login")
def login_admin(data: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = crud.authenticate_admin(db, data.username, data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": admin.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}