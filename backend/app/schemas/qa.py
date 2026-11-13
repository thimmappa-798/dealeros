
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class QACitation(BaseModel):
    exception_id: int
    normalized_reference: str
    reason_code: str
    system_a_source_id: str | None = None
    system_b_entry_ids: list[str] = Field(default_factory=list)


class QuestionResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[QACitation] = Field(default_factory=list)
