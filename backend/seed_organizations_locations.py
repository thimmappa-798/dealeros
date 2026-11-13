
import csv

from app.database import SessionLocal
from app.models import Organization, Location


def load_locations():
    with open(
        "app/data/locations.csv",
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def seed_data():

    db = SessionLocal()

    try:
        rows = load_locations()

        for row in rows:

            org_external_id = row["org_id"]

            # Find or create the organization
            organization = db.query(Organization).filter(
                Organization.external_id == org_external_id
            ).first()

            if not organization:
                organization = Organization(
                    external_id=org_external_id,
                    name=f"Organization {org_external_id}"
                )

                db.add(organization)
                db.flush()

            # Find or create the location
            location = db.query(Location).filter(
                Location.organization_id == organization.id,
                Location.location_code == row["location_id"]
            ).first()

            if not location:
                location = Location(
                    location_code=row["location_id"],
                    name=row["location_name"],
                    organization_id=organization.id
                )

                db.add(location)

        db.commit()

        print("Organizations and locations imported successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
