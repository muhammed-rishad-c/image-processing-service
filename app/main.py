import os
import uuid
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.config import ORIGINALS_DIR
from app.database import init_db, get_session
from app.models import (
    User, UserCreate, UserResponse, Token,
    ImageRecord, ImageRecordResponse
)
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from app.image_engine import process_image



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Image Processing Service",
    description="FastAPI backend for uploading, resizing, rotating, and managing images with JWT auth.",
    version="1.0.0",
    lifespan=lifespan
)

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=Token)
def login(user_data: UserCreate, session: Session = Depends(get_session)):
    
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")



@app.post("/images/upload", response_model=ImageRecordResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WebP are allowed."
        )

    file_id = uuid.uuid4()
    file_ext = os.path.splitext(file.filename)[1].lower()
    saved_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(ORIGINALS_DIR, saved_filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    image_record = ImageRecord(
        id=file_id,
        user_id=current_user.id,
        original_name=file.filename,
        file_path=file_path,
        mime_type=file.content_type,
        size=len(contents)
    )

    session.add(image_record)
    session.commit()
    session.refresh(image_record)

    return image_record


@app.get("/images", response_model=List[ImageRecordResponse])
def list_images(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(ImageRecord).where(ImageRecord.user_id == current_user.id)
    images = session.exec(statement).all()
    return images


@app.get("/images/{image_id}/render")
def render_image(
    image_id: uuid.UUID,
    w: Optional[int] = Query(None, description="Width in pixels"),
    h: Optional[int] = Query(None, description="Height in pixels"),
    rotate: Optional[int] = Query(None, description="Rotation angle in degrees"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    
    statement = select(ImageRecord).where(
        ImageRecord.id == image_id,
        ImageRecord.user_id == current_user.id
    )
    image_record = session.exec(statement).first()

    if not image_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found or access forbidden"
        )

    try:
        output_path = process_image(
            original_path=image_record.file_path,
            width=w,
            height=h,
            rotate=rotate
        )
        return FileResponse(output_path, media_type=image_record.mime_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image transformation failed: {str(e)}"
        )