from pydantic import EmailStr
from sqlalchemy.orm import Session
from app import models, schemas
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

# --- USER CRUD ---

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = generate_password_hash(user.password)
    # 👇 FIX: Added 'email=user.email' to save the email address
    db_user = models.User(
        username=user.username, 
        email=user.email,  
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not check_password_hash(user.password, password):
        return None
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(func.lower(models.User.email) == func.lower(email)).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def update_user_password(db: Session, user_id: int, new_password: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.commit()
        db.refresh(user)
    return user

def verify_user_email(db: Session, email: str):
    user = get_user_by_email(db, email)
    if user:
        user.is_verified = 1
        db.commit()
        db.refresh(user)
    return user

# --- BOOK CRUD (No changes needed here) ---

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# ... (rest of book CRUD functions: get_books, get_book, update_book, delete_book) ...