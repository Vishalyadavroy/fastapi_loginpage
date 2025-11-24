from datetime import datetime, timedelta
from fastapi import APIRouter
from jose import JWTError, jwt

SECRET_KEY = "agdagfasgf564576sagfakgfsaf57asfjsagfas5f765af5dsa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# def create_reset_token(email: str):
#     expire = datetime.utcnow() + timedelta(minutes=15)
#     data = {"sub": email, "exp": expire}
#     return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# In app/auth.py
def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=15)
    data = {"sub": email, "exp": expire} 
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data["sub"]
    except:
        return None
# phkt rksm rzqs iwxl