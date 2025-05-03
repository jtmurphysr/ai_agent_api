# db.py
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
import os
import getpass
import sys

# Get the current system username
system_user = getpass.getuser()

# Try to use PostgreSQL, fall back to SQLite for development
try:
    # Get database URL from environment variable or use default
    DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{system_user}:@localhost/ai_agent")
    engine = create_engine(DATABASE_URL)
    # Test connection
    with engine.connect() as conn:
        pass
    print("Connected to PostgreSQL successfully")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    print("Falling back to SQLite for development")
    DATABASE_URL = "sqlite:///./ai_agent.db"
    engine = create_engine(DATABASE_URL)
    # Need to adjust some column types for SQLite
    from sqlalchemy.types import JSON
    # SQLite doesn't support UUID or JSONB natively
    UUID_TYPE = String
    JSON_TYPE = JSON
else:
    UUID_TYPE = UUID(as_uuid=True)
    JSON_TYPE = JSONB

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_metadata = Column(JSON_TYPE, default={})
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID_TYPE, ForeignKey("sessions.session_id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    embedding_status = Column(String, default="pending")
    message_metadata = Column(JSON_TYPE, default={})
    session = relationship("Session", back_populates="messages")

class EmbeddingJob(Base):
    __tablename__ = "embedding_jobs"
    job_id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="running")
    messages_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 