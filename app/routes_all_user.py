from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud

router = APIRouter(prefix="/admin-panel", tags=["Admin Operations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/all-users")
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return {"total_users": len(users), "users": users}


@router.get("/all-admins")
def get_all_admins(db: Session = Depends(get_db)):
    admins = crud.get_all_admins(db)
    return {"total_admins": len(admins), "admins": admins}
