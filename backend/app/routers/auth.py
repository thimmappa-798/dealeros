
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.service.auth import verify_password, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



@router.post("/login")
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.authenticate_user(
                :email,
                :org_code
            )
        """),
        {"email": data.email, "org_code": data.organization_code}
    ).mappings().first()

    if not result or not verify_password(
        data.password,
        result["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or organization code"
        )

    access_token = create_access_token(
        user_id=result["user_id"],
        organization_id=result["organization_id"]
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=1800,
        path="/"
    )

    return {"message": "Login successful"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )

    return {"message": "Logout successful"}


