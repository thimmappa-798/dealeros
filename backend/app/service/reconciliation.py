
import re
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    SystemARecord,
    SystemBRecord,
    ReconciliationException
)


# --------------------------------------------------
# 1. NORMALIZE RECORD REFERENCES
# --------------------------------------------------

def normalize_reference(value):

    value = value.strip().upper()
    value = re.sub(r"[\s-]+", "", value)

    if value.isdigit():
        value = "REC" + value

    return value


# --------------------------------------------------
# 2. CREATE AN EXCEPTION
# --------------------------------------------------

def add_exception(
    db,
    organization_id,
    location_id,
    reference,
    reason_code,
    description,
    system_a_source_id=None,
    system_b_entry_ids=None,
    evidence=None
):

    exception = ReconciliationException(
        organization_id=organization_id,
        location_id=location_id,
        normalized_reference=reference,
        reason_code=reason_code,
        description=description,
        system_a_source_id=system_a_source_id,
        system_b_entry_ids=system_b_entry_ids or [],
        evidence=evidence or {},
        status="OPEN"
    )

    db.add(exception)


# --------------------------------------------------
# 3. MAIN RECONCILIATION FUNCTION
# --------------------------------------------------

def reconcile_organization(db: Session, organization_id: int):

    # Read only this organization's records
    system_a_records = db.query(SystemARecord).filter(
        SystemARecord.organization_id == organization_id
    ).all()

    system_b_records = db.query(SystemBRecord).filter(
        SystemBRecord.organization_id == organization_id
    ).all()

    # Group records using normalized references
    a_grouped = {
        normalize_reference(record.source_record_id): record
        for record in system_a_records
    }

    b_grouped = defaultdict(list)

    for record in system_b_records:
        reference = normalize_reference(record.record_ref)
        b_grouped[reference].append(record)

    # Replace previous results for this organization
    db.query(ReconciliationException).filter(
        ReconciliationException.organization_id == organization_id
    ).delete(synchronize_session=False)

    exception_count = 0

    # --------------------------------------------------
    # 4. CHECK EVERY SYSTEM A RECORD
    # --------------------------------------------------

    for reference, a_record in a_grouped.items():

        b_records = b_grouped.get(reference, [])

        # Missing from System B
        if not b_records:

            add_exception(
                db,
                organization_id,
                a_record.location_id,
                reference,
                "MISSING_IN_SYSTEM_B",
                "Record exists in System A but not in System B.",
                system_a_source_id=a_record.source_record_id
            )

            exception_count += 1
            continue

        # Detect exact duplicate System B entries.
        # entry_id is excluded because duplicate source rows
        # naturally have different entry IDs.

        unique_records = []
        seen = set()
        duplicate_entry_ids = []

        for record in b_records:

            signature = (
                record.location_id,
                record.recorded_on,
                record.value,
                record.raw_value,
                record.label
            )

            if signature in seen:
                duplicate_entry_ids.append(record.entry_id)
            else:
                seen.add(signature)
                unique_records.append(record)

        entry_ids = [
            record.entry_id for record in b_records
        ]

        # Duplicate entry exception
        if duplicate_entry_ids:

            add_exception(
                db,
                organization_id,
                a_record.location_id,
                reference,
                "DUPLICATE_ENTRY",
                "System B contains identical duplicate entries.",
                system_a_source_id=a_record.source_record_id,
                system_b_entry_ids=entry_ids,
                evidence={
                    "duplicate_entry_ids": duplicate_entry_ids
                }
            )

            exception_count += 1

        # Location mismatch
        if any(
            record.location_id != a_record.location_id
            for record in unique_records
        ):

            add_exception(
                db,
                organization_id,
                a_record.location_id,
                reference,
                "LOCATION_MISMATCH",
                "System A and System B have different locations.",
                system_a_source_id=a_record.source_record_id,
                system_b_entry_ids=entry_ids
            )

            exception_count += 1

        # Date mismatch
        if any(
            record.recorded_on != a_record.event_date
            for record in unique_records
        ):

            add_exception(
                db,
                organization_id,
                a_record.location_id,
                reference,
                "DATE_MISMATCH",
                "System A and System B have different dates.",
                system_a_source_id=a_record.source_record_id,
                system_b_entry_ids=entry_ids
            )

            exception_count += 1

        # Invalid amount check
        invalid_records = [
            record
            for record in unique_records
            if record.value is None
        ]

        if invalid_records:

            add_exception(
                db,
                organization_id,
                a_record.location_id,
                reference,
                "INVALID_AMOUNT",
                "One or more System B entries have an invalid amount.",
                system_a_source_id=a_record.source_record_id,
                system_b_entry_ids=entry_ids,
                evidence={
                    "invalid_entries": [
                        {
                            "entry_id": record.entry_id,
                            "raw_value": record.raw_value
                        }
                        for record in invalid_records
                    ]
                }
            )

            exception_count += 1

        else:

            # Sum unique entries only.
            # This allows valid split entries.

            b_total = sum(
                (record.value for record in unique_records),
                Decimal("0")
            )

            if b_total != a_record.total_value:

                add_exception(
                    db,
                    organization_id,
                    a_record.location_id,
                    reference,
                    "VALUE_MISMATCH",
                    "Combined System B amount does not match System A.",
                    system_a_source_id=a_record.source_record_id,
                    system_b_entry_ids=entry_ids,
                    evidence={
                        "system_a_total": str(a_record.total_value),
                        "system_b_total": str(b_total)
                    }
                )

                exception_count += 1

    # --------------------------------------------------
    # 5. FIND RECORDS THAT EXIST ONLY IN SYSTEM B
    # --------------------------------------------------

    for reference, b_records in b_grouped.items():

        if reference not in a_grouped:

            first_record = b_records[0]

            add_exception(
                db,
                organization_id,
                first_record.location_id,
                reference,
                "UNMATCHED_IN_SYSTEM_A",
                "Record exists in System B but not in System A.",
                system_b_entry_ids=[
                    record.entry_id for record in b_records
                ]
            )

            exception_count += 1

    # Save all exceptions
    db.flush()

    return {
        "organization_id": organization_id,
        "system_a_records": len(system_a_records),
        "system_b_records": len(system_b_records),
        "exceptions_created": exception_count
    }
