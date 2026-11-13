
from getpass import getpass
from passlib.context import CryptContext

from app.database import AdminSessionLocal
from app.models import User

password_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def main():
    db = AdminSessionLocal()

    try:
        email = "admin-a@dealeros.local"

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:
            print("Demo user not found.")
            return

        new_password = getpass("Enter your new password: ")
        confirm_password = getpass("Confirm your new password: ")

        if new_password != confirm_password:
            print("Passwords do not match.")
            return

        user.hashed_password = password_context.hash(new_password)
        db.commit()

        print("Password reset successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
