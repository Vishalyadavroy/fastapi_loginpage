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


router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(crud.models.User).filter(crud.models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    crud.create_user(db, user)
    return {"message": "User created successfully"}

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": auth_user.username })
    return {"access_token": token, "token_type": "bearer"}



#new added 
@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = crud.create_user(db, user)

    token = create_reset_token(user.email)
    verify_link = f"http://localhost:8000/auth/verify-email?token={token}"

    send_email(user.email, "Verify Email", f"Click to verify: {verify_link}")

    return {"message": "User created. Check email for verification link."}



@router.post("/change-password")
def change_password(data: schemas.ChangePassword,
                    db: Session = Depends(get_db),
                    token: str = Depends(oauth2_scheme)):
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    user = crud.get_user_by_username(db, username)

    if not check_password_hash(user.password, data.old_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    crud.update_user_password(db, user.id, data.new_password)

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPassword, db: Session = Depends(get_db)):
    print("Received email:", data.email)
    user = crud.get_user_by_email(db, data.email)
    print("User found:", user)

    if not user:
        print("User not found in the database")
        raise HTTPException(status_code=404, detail="Email not found")

    token = create_reset_token(user.email)
    link = f"http://localhost:8000/auth/reset-password?token={token}"

    send_email(user.email, "Reset Password", f"Reset here: {link}")

    return {"message": "Reset password email sent"}



@router.post("/reset-password")
def reset_password(data: schemas.ResetPassword, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.get_user_by_email(db, email)
    
    # 👇 FIX: Check if the user exists after getting the email from the token
    if not user:
        # If the user was deleted after the token was issued, or the email is wrong.
        raise HTTPException(status_code=400, detail="User not found or deleted.")

    # This line is now safe because 'user' is guaranteed to be a valid object
    crud.update_user_password(db, user.id, data.new_password)

    return {"message": "Password reset successfully"}


# @router.post("/login", response_model=schemas.Token)
# def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
#     auth_user = crud.authenticate_user(db, user.username, user.password)
#     if not auth_user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = create_access_token({"sub": auth_user.username})
#     return {"access_token": token, "token_type": "bearer"}






@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    crud.verify_user_email(db, email)
    return {"message": "Email verified successfully"}


# this router for Admin

# router = APIRouter(prefix="/admin" , tags=["Admin"])
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/dashboard")
# def admin_dashboard(token: str = Depends(admin_required)):
#     return {"message": "Welcome Admin!"}



# @router.post("/create")
# def create_admin(admin:schemas.AdminCreate ,db:Session = Depends(get_db)):
#     existing = crud.get_admin_y_user(db, admin.username)
#     if existing:
#          raise HTTPException(status_code=400 , detail="Admin username already exists")
#     return crud.create_admin(db, admin)

# @router.post("/login")
# def login_admin(data: schemas.AdminLogin, db: Session = Depends(get_db)):
#     admin = crud.authenticate_admin(db, data.username, data.password)
#     if not admin:
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     token = create_access_token({"sub": admin.username, "role": "admin"})
#     return {"access_token": token, "token_type": "bearer"}