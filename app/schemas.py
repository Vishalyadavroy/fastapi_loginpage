from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("username")
    def username_length(cls, v):
        if len(v) < 5:
            raise ValueError("Username must be at least 5 characters long")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class BookBase(BaseModel):
    title: str
    author: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str

# //otp section 
class SendOTP(BaseModel):
    email: EmailStr

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str
