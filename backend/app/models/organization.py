
from sqlalchemy import Column, Integer, String
from app.database import Base


class Organization(Base):

    __tablename__ = "organizations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    external_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    name = Column(
        String(255),
        nullable=False
    )
