
from datetime import date

from sqlalchemy import (
    Integer,
    String,
    Text,
    Date,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column, relationship
from pgvector.sqlalchemy import VECTOR

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    email = mapped_column(String(255), nullable=False, unique=True)
    hashed_password = mapped_column(String(255), nullable=False)

    job_applications = relationship(
        "JobApplication",
        back_populates="user"
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = mapped_column(Integer, primary_key=True)
    company = mapped_column(String(150), nullable=False)
    job_title = mapped_column(String(150), nullable=False)
    status = mapped_column(String(50), default="applied", nullable=False)
    job_url = mapped_column(String(500), nullable=True)
    notes = mapped_column(Text, nullable=True)
    job_description = mapped_column(Text, nullable=True)
    applied_date = mapped_column(Date, default=date.today, nullable=False)
    user_id = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    salary = mapped_column(Integer, nullable=True)

    user = relationship(
        "User",
        back_populates="job_applications"
    )

    chunks = relationship(
        "JobApplicationChunk",
        back_populates="job_application",
        cascade="all, delete-orphan"
    )


class JobApplicationChunk(Base):
    __tablename__ = "job_application_chunks"

    __table_args__ = (
        UniqueConstraint(
            "job_application_id",
            "chunk_index",
            name="uq_job_application_chunk_index"
        ),
    )

    id = mapped_column(Integer, primary_key=True)

    job_application_id = mapped_column(
        Integer,
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index = mapped_column(Integer, nullable=False)

    content = mapped_column(Text, nullable=False)

    embedding = mapped_column(VECTOR(768), nullable=False)

    job_application = relationship(
        "JobApplication",
        back_populates="chunks"
    )
