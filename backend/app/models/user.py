"""
User Model
==========
Database model for user authentication and authorization.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role (admin, architect, engineer, viewer)
        is_active: Account active status
        is_superuser: Superuser privileges
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("ix_users_email_lower", func.lower(email)),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Project(Base):
    """
    Project model for storing architectural projects.
    
    Attributes:
        id: Unique project identifier
        name: Project name
        description: Project description
        owner_id: Foreign key to user
        status: Project status (draft, active, completed, archived)
        settings: JSON settings for the project
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="draft")
    settings: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    designs: Mapped[List["Design"]] = relationship(
        "Design",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Design(Base):
    """
    Design model for storing generated architectural designs.
    
    Attributes:
        id: Unique design identifier
        project_id: Foreign key to project
        name: Design name
        design_data: JSON design data (geometry, layout, etc.)
        scores: JSON scores (safety, stability, efficiency, utilization)
        status: Design status
        created_at: Creation timestamp
    """
    
    __tablename__ = "designs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    design_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    scores: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    status: Mapped[str] = mapped_column(String(50), default="generated")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="designs")