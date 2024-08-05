from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_PATH

# Database setup
DATABASE_URL = DB_PATH
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database (usually done once, e.g., in a startup event)
def init_db():
    Base.metadata.create_all(bind=engine)