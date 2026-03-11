from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# -- ROLE ------------------------------------------
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- USER ------------------------------------------
class UserBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    email: str
    password: str
    role_id: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    role_id: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserWithRole(UserResponse):
    role: RoleResponse


# -- AUTH ------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# -- SESSION ---------------------------------------
class SessionResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    channel: str
    is_active: bool
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
