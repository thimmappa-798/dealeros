from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint
)

from app.database import Base


class Location(Base):

    __tablename__ = "locations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    location_code = Column(
        String(50),
        nullable=False
    )

    name = Column(
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
            "location_code",
            name="uq_location_code_per_organization"
        ),
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_location_id_organization"
        ),
    )