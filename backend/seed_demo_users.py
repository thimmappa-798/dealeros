
from getpass import getpass

from passlib.context import CryptContext

from app.database import AdminSessionLocal
from app.models import Organization, User


password_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def main():

    db = AdminSessionLocal()

    try:
        organizations = {
            org.external_id: org
            for org in db.query(Organization).all()
        }

        demo_users = [
            {
                "username": "Admin ORG-A",
                "email": "admin-a@dealeros.local",
                "organization": "ORG-A",
            },
            {
                "username": "Admin ORG-B",
                "email": "admin-b@dealeros.local",
                "organization": "ORG-B",
            },
        ]

        for user_data in demo_users:

            email = user_data["email"]

            existing_user = db.query(User).filter(
                User.email == email
            ).first()

            if existing_user:
                print(f"{email} already exists. Skipping.")
                continue

            password = getpass(
                f"Enter password for {email}: "
            )

            hashed_password = password_context.hash(password)

            user = User(
                username=user_data["username"],
                email=email,
                hashed_password=hashed_password,
                organization_id=organizations[
                    user_data["organization"]
                ].id
            )

            db.add(user)

        db.commit()

        print("Demo users created successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
