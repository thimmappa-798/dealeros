
from app.database import AdminSessionLocal
from app.models import Organization
from app.service.reconciliation import reconcile_organization


def main():

    db = AdminSessionLocal()

    try:
        organizations = db.query(Organization).order_by(
            Organization.external_id
        ).all()

        for organization in organizations:

            result = reconcile_organization(
                db,
                organization.id
            )

            print(f"\nOrganization: {organization.external_id}")
            print("System A records:", result["system_a_records"])
            print("System B records:", result["system_b_records"])
            print("Exceptions created:", result["exceptions_created"])

        db.commit()

        print("\nReconciliation completed successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
