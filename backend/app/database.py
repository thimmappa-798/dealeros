
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Load database credentials from .env
load_dotenv()

# Admin connection: used by Alembic and database administration
ADMIN_DATABASE_URL = os.getenv("ADMIN_DATABASE_URL")

# Application connection: used by FastAPI
APP_DATABASE_URL = os.getenv("APP_DATABASE_URL")


if not ADMIN_DATABASE_URL:
    raise ValueError("ADMIN_DATABASE_URL is missing from .env")

if not APP_DATABASE_URL:
    raise ValueError("APP_DATABASE_URL is missing from .env")


# Create database engines
admin_engine = create_engine(ADMIN_DATABASE_URL)

app_engine = create_engine(APP_DATABASE_URL)


# Database sessions
AdminSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=admin_engine
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=app_engine
)


# Base class for database models
Base = declarative_base()
