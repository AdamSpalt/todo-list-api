from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
from fastapi import HTTPException
import os

# 1. Load environment variables from .env
if load_dotenv(override=True):
    print("\n✅ .env file loaded successfully")
else:
    print("\n⚠️  .env file NOT found. Using system environment variables.")

# 2. Get the Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# DEBUG: Print the host we are trying to connect to (hides password)
if DATABASE_URL:
    safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "INVALID_URL"
    print(f"\n🔌 DEBUG: Connecting to Database Host: {safe_url}\n")

# Fix for SQLAlchemy (it requires 'postgresql://' but some providers give 'postgres://')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Create the Database Engine (Safely)
engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL, echo=True)
    except Exception as e:
        print(f"❌ Database connection failed to initialize: {e}")

def create_db_and_tables():
    """Creates the tables in the database based on the SQLModel metadata."""
    if engine:
        SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to provide a database session to endpoints."""
    if not engine:
        raise HTTPException(status_code=500, detail="Database not configured. Check DATABASE_URL env var.")
    with Session(engine) as session:
        yield session