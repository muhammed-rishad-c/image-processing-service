# Image Processing Service API

A high-performance, asynchronous RESTful API built with **FastAPI**, **SQLModel**, **PostgreSQL**, **JWT Authentication**, and **Pillow** for uploading, managing, and dynamically transforming images (resizing, rotating, cropping).

---

## 🛠️ Features

- **JWT User Authentication:** Secure endpoints with user registration, login, and Bearer token verification.
- **Image Upload Management:** Validate file types (JPEG, PNG, WebP) and save uploaded files securely with metadata in PostgreSQL.
- **Dynamic Image Transformations:** Perform real-time image manipulations on demand:
  - **Resize:** Adjust width and height with optional aspect ratio retention.
  - **Rotate:** Rotate images by specific degrees (`90°`, `180°`, `270°`, etc.).
  - **Format Conversion:** Render and convert images across different formats (`JPEG`, `PNG`, `WEBP`).
- **Database Management:** Uses **SQLModel** (SQLAlchemy + Pydantic) for clean database migrations and ORM queries.

---

## 📁 Project Structure

```text
image_processing_service/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point & route registration
│   ├── config.py          # Environment variables & settings
│   ├── database.py        # Database engine setup & session dependencies
│   ├── models.py          # SQLModel schemas for User and Image entities
│   ├── auth.py            # Password hashing & JWT generation/decoding
│   ├── dependencies.py    # Request dependencies (get_current_user, get_session)
│   ├── image_engine.py    # Pillow-based image manipulation logic
│   └── routers/
│       ├── auth_router.py # Auth endpoints (/auth/register, /auth/login)
│       └── image_router.py# Image endpoints (/images/upload, /images/{id}/render)
├── uploads/               # Directory where raw uploaded images are stored
├── .env                   # Environment variables (DB connection, JWT secret)
├── .gitignore
├── README.md
└── requirements.txt       # Project dependencies