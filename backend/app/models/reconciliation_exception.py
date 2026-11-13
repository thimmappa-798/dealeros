
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
    DateTime,
    JSON,
    func
)

from app.database import Base


class ReconciliationException(Base):

    __tablename__ = "reconciliation_exceptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
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

    normalized_reference = Column(
        String(100),
        nullable=False
    )

    reason_code = Column(
        String(50),
        nullable=False
    )

    description = Column(
        String(500),
        nullable=False
    )

    system_a_source_id = Column(
        String(50),
        nullable=True
    )

    system_b_entry_ids = Column(
        JSON,
        nullable=True
    )

    evidence = Column(
        JSON,
        nullable=False,
        default=dict
    )

    status = Column(
        String(20),
        nullable=False,
        default="OPEN"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "normalized_reference",
            "reason_code",
            name="uq_exception_per_org_reference_reason"
        ),

        ForeignKeyConstraint(
            ["location_id", "organization_id"],
            ["locations.id", "locations.organization_id"],
            name="fk_exception_location_organization"
        ),
    )
