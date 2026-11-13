
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.qa import QuestionRequest, QuestionResponse
from app.service.qa import answer_question


router = APIRouter(
    prefix="/qa",
    tags=["Q&A"]
)


@router.post("/ask", response_model=QuestionResponse)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = answer_question(
        db=db,
        organization_id=current_user["organization_id"],
        question=request.question
    )

    return result
