
import httpx

from sqlalchemy import text

from app.database import SessionLocal
from app.service import qa


def set_organization_context(db, organization_id):
    db.execute(
        text("SELECT set_config('app.current_org', :org_id, true)"),
        {"org_id": str(organization_id)}
    )


def test_value_mismatch_answer_has_source_citations(monkeypatch):
    # Avoid depending on Ollama during this database test.
    monkeypatch.setattr(
        qa,
        "detect_intent",
        lambda question: "count_value_mismatches"
    )

    with SessionLocal() as db:
        set_organization_context(db, 1)

        result = qa.answer_question(
            db=db,
            organization_id=1,
            question="How many value mismatches are there?"
        )

        assert result["grounded"] is True
        assert "3 value mismatches" in result["answer"]
        assert len(result["citations"]) == 3

        for citation in result["citations"]:
            assert citation["exception_id"] is not None
            assert citation["normalized_reference"]
            assert citation["reason_code"] == "VALUE_MISMATCH"


def test_unsupported_question_is_refused(monkeypatch):
    monkeypatch.setattr(
        qa,
        "detect_intent",
        lambda question: None
    )

    with SessionLocal() as db:
        result = qa.answer_question(
            db=db,
            organization_id=1,
            question="Who is the CEO of Microsoft?"
        )

        assert result["grounded"] is False
        assert result["citations"] == []
        assert "cannot answer" in result["answer"].lower()


def test_ollama_unavailable_returns_no_intent(monkeypatch):
    def simulate_ollama_failure(*args, **kwargs):
        raise httpx.ConnectError("Ollama unavailable")

    monkeypatch.setattr(
        qa.httpx,
        "post",
        simulate_ollama_failure
    )

    result = qa.detect_intent(
        "How many value mismatches are there?"
    )

    assert result is None
