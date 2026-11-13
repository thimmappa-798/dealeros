
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint
)

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_user_email_per_organization"
        ),
    )
