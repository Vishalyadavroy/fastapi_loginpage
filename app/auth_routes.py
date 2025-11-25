from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, crud
from app.auth import ALGORITHM, SECRET_KEY, create_access_token, create_reset_token, verify_reset_token
from app.email_utils import send_email
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from werkzeug.security import check_password_hash
from app.auth import SECRET_KEY, ALGORITHM


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

    token = create_access_token({"sub": auth_user.username})
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


# otp auth
@router.post("/send-otp")
def send_otp(data: schemas.SendOTP, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp = crud.generate_otp()
    crud.save_otp(db, data.email, otp)

    message = f"Your OTP for email verification is: {otp}. It is valid for 10 minutes."
    send_email(data.email, "Your OTP Code", message)

    return {"message": "OTP sent successfully to email"}


# //otp verify api
@router.post("/verify-otp")
def verify_otp(data: schemas.VerifyOTP, db: Session = Depends(get_db)):
    valid = crud.verify_otp_code(db, data.email, data.otp)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"message": "OTP Verified Successfully"}
