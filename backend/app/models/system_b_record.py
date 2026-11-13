
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    ForeignKeyConstraint
)

from app.database import Base


class SystemBRecord(Base):

    __tablename__ = "system_b_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    entry_id = Column(
        String(100),
        nullable=False
    )

    record_ref = Column(
        String(100),
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

    recorded_on = Column(
        Date,
        nullable=False
    )

    value = Column(
        Numeric(14, 2),
        nullable=True
    )
    raw_value = Column(
    String(100),
    nullable=True
    )

    label = Column(
        String(255),
        nullable=True
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["location_id", "organization_id"],
            ["locations.id", "locations.organization_id"],
            name="fk_system_b_location_organization"
        ),
    )
