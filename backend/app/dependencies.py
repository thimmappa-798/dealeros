
from fastapi import Depends, HTTPException, status
from fastapi import Cookie
from jose import jwt, JWTError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.service.auth import SECRET_KEY, ALGORITHM



def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])
        organization_id = int(payload["org_id"])

    except (JWTError, KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    db.execute(
        text("SELECT set_config('app.current_org', :org_id, true)"),
        {"org_id": str(organization_id)}
    )

    return {
        "user_id": user_id,
        "organization_id": organization_id
    }
