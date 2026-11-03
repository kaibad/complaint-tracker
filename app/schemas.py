from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Category, Role, Status


class ComplaintCreate(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10)
    category: Category
    citizen_name: str = Field(min_length=2, max_length=80)
    phone: str | None = Field(default=None, pattern=r"^\d{7,15}$")


class ComplaintUpdate(BaseModel):
    status: Status
    remarks: str | None = None


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: Category
    citizen_name: str
    phone: str | None
    owner_id: int | None
    status: Status
    remarks: str | None
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Role


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
