import uuid
from typing import Optional, List
from datetime import datetime,timezone
from sqlmodel import SQLModel, Field, Relationship

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # One-to-Many Relationship
    images: List["ImageRecord"] = Relationship(back_populates="owner")
    
class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    
class ImageRecordBase(SQLModel):
    original_name: str
    mime_type: str
    size: int


class ImageRecord(ImageRecordBase, table=True):
    __tablename__ = "images"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    file_path: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    owner: Optional[User] = Relationship(back_populates="images")


class ImageRecordResponse(ImageRecordBase):
    id: uuid.UUID
    created_at: datetime