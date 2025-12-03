import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy import create_engine, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


current_file = Path(__file__).absolute()

BASE_DIR = current_file.parent

DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

DB_FILE = os.path.join(DB_DIR, "gemini_explainer.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    uploads: Mapped[List["Upload"]] = relationship(
        "Upload",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    upload_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    finish_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    summary_level: Mapped[str] = mapped_column(String(50), nullable=False, default="comprehensive")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    user: Mapped[Optional["User"]] = relationship("User", back_populates="uploads")

    def __init__(self, filename: str, user_id: Optional[int] = None, summary_level: str = "comprehensive", language: str = "en"):
        self.uid = str(uuid.uuid4())
        self.filename = filename
        self.user_id = user_id
        self.upload_time = datetime.utcnow()
        self.status = "uploaded"
        self.summary_level = summary_level
        self.language = language

    @property
    def upload_path(self) -> str:
        """Compute the path of the uploaded file based on the UID."""
        # FIXED: Use the correct BASE_DIR
        uploads_dir = os.path.join(BASE_DIR, "shared", "uploads")
        return os.path.join(uploads_dir, f"{self.uid}.pptx")

    @property
    def output_path(self) -> str:
        """Compute the path of the output file based on the UID."""
        # FIXED: Use the correct BASE_DIR
        outputs_dir = os.path.join(BASE_DIR, "shared", "outputs")
        return os.path.join(outputs_dir, f"{self.uid}.json")

    @property
    def is_pending(self) -> bool:
        """Check if upload is in a pending state."""
        return self.status in ["uploaded", "processing"]

    @property
    def is_done(self) -> bool:
        """Check if upload is completed successfully."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if upload has failed."""
        return self.status == "failed"

    def set_status_processing(self):
        """Mark upload as being processed."""
        self.status = "processing"

    def set_status_completed(self):
        """Mark upload as completed and set finish time."""
        self.status = "completed"
        self.finish_time = datetime.utcnow()

    def set_status_failed(self, error_message: str):
        """Mark upload as failed with error message."""
        self.status = "failed"
        self.error_message = error_message
        self.finish_time = datetime.utcnow()


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Get a new database session."""
    return SessionLocal()


class UploadStatus:
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"