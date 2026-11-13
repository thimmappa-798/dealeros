
import csv
from datetime import date
from decimal import Decimal, InvalidOperation

from app.database import SessionLocal
from app.models import Location, SystemARecord, SystemBRecord


# --------------------------------------------------
# 1. HELPER FUNCTIONS
# --------------------------------------------------

def load_csv(path):
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def parse_amount(value):
    """
    Convert a CSV amount into Decimal.

    Examples:
    '1,25,400.00' -> Decimal('125400.00')
    ''            -> None
    'invalid'     -> None
    """

    value = value.strip().replace(",", "")

    if not value:
        return None

    try:
        amount = Decimal(value)

        if not amount.is_finite():
            return None

        return amount

    except InvalidOperation:
        return None


def get_location(db, location_code):
    location = db.query(Location).filter(
        Location.location_code == location_code
    ).first()

    if not location:
        raise ValueError(
            f"Location not found: {location_code}"
        )

    return location


# --------------------------------------------------
# 2. IMPORT SYSTEM A
# --------------------------------------------------

def import_system_a(db):

    rows = load_csv("app/data/system_a.csv")

    imported = 0
    skipped = 0

    for row in rows:

        location = get_location(
            db,
            row["location_id"]
        )

        organization_id = location.organization_id
        source_record_id = row["record_id"]

        # Avoid importing the same record twice
        existing = db.query(SystemARecord).filter(
            SystemARecord.organization_id == organization_id,
            SystemARecord.source_record_id == source_record_id
        ).first()

        if existing:
            skipped += 1
            continue

        base_value = parse_amount(row["base_value"])
        adjustment = parse_amount(row["adjustment"])
        total_value = parse_amount(row["total_value"])

        if None in (base_value, adjustment, total_value):
            raise ValueError(
                f"Invalid System A amount in record {source_record_id}"
            )

        record = SystemARecord(
            source_record_id=source_record_id,
            organization_id=organization_id,
            location_id=location.id,
            event_date=date.fromisoformat(row["event_date"]),
            category_code=row["category_code"],
            actor_id=row["actor_id"],
            base_value=base_value,
            adjustment=adjustment,
            total_value=total_value,
            state=row["state"]
        )

        db.add(record)
        imported += 1

    print(
        f"System A: {imported} imported, {skipped} skipped"
    )


# --------------------------------------------------
# 3. IMPORT SYSTEM B
# --------------------------------------------------

def import_system_b(db):

    rows = load_csv("app/data/system_b.csv")

    imported = 0
    skipped = 0

    for row in rows:

        location = get_location(
            db,
            row["location_id"]
        )

        organization_id = location.organization_id
        entry_id = row["entry_id"]

        # Avoid importing the same entry twice
        existing = db.query(SystemBRecord).filter(
            SystemBRecord.organization_id == organization_id,
            SystemBRecord.entry_id == entry_id
        ).first()

        if existing:
            skipped += 1
            continue

        original_value = row["value"]
        parsed_value = parse_amount(original_value)

        record = SystemBRecord(
            entry_id=entry_id,
            record_ref=row["record_ref"],
            organization_id=organization_id,
            location_id=location.id,
            recorded_on=date.fromisoformat(row["recorded_on"]),
            value=parsed_value,
            raw_value=original_value,
            label=row["label"]
        )

        db.add(record)
        imported += 1

    print(
        f"System B: {imported} imported, {skipped} skipped"
    )


# --------------------------------------------------
# 4. RUN IMPORT
# --------------------------------------------------

def main():

    db = SessionLocal()

    try:
        import_system_a(db)
        import_system_b(db)

        db.commit()

        print("\nSource records imported successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
