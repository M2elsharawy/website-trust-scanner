import uuid

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    preferred_lang: str = "ar"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("preferred_lang")
    @classmethod
    def lang_valid(cls, v: str) -> str:
        if v not in {"ar", "en"}:
            raise ValueError("preferred_lang must be 'ar' or 'en'")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    preferred_lang: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
