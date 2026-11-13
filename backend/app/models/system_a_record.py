
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint
)

from app.database import Base


class SystemARecord(Base):

    __tablename__ = "system_a_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    source_record_id = Column(
        String(50),
        nullable=False
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False
    )

    location_id = Column(
        Integer,
        nullable=False
    )

    event_date = Column(
        Date,
        nullable=False
    )

    category_code = Column(
        String(50),
        nullable=False
    )

    actor_id = Column(
        String(50),
        nullable=False
    )

    base_value = Column(
        Numeric(14, 2),
        nullable=False
    )

    adjustment = Column(
        Numeric(14, 2),
        nullable=False
    )

    total_value = Column(
        Numeric(14, 2),
        nullable=False
    )

    state = Column(
        String(50),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "source_record_id",
            name="uq_system_a_record_per_organization"
        ),
        ForeignKeyConstraint(
            ["location_id", "organization_id"],
            ["locations.id", "locations.organization_id"],
            name="fk_system_a_location_organization"
        ),
    )
