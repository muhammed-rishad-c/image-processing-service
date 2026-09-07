import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM= "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
DATABASE_URL = os.getenv("DATABASE_URL")

ORIGINALS_DIR="uploads/originals"
TRANSFORMED_DIR="uploads/transformed"

os.makedirs(ORIGINALS_DIR, exist_ok=True)
os.makedirs(TRANSFORMED_DIR, exist_ok=True)

