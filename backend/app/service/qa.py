
import json
import os

import httpx
from sqlalchemy.orm import Session

from app.models import ReconciliationException

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"


SUPPORTED_INTENTS = {
    "count_total_exceptions": {
        "reason_code": None,
        "label": "total exceptions"
    },
    "count_value_mismatches": {
        "reason_code": "VALUE_MISMATCH",
        "label": "value mismatches"
    },
    "count_duplicate_entries": {
        "reason_code": "DUPLICATE_ENTRY",
        "label": "duplicate entries"
    },
    "count_missing_in_system_b": {
        "reason_code": "MISSING_IN_SYSTEM_B",
        "label": "records missing in System B"
    },
    "count_unmatched_in_system_a": {
        "reason_code": "UNMATCHED_IN_SYSTEM_A",
        "label": "records unmatched in System A"
    }
}


def question_matches_intent(question: str, intent: str):
    question = question.lower()

    intent_keywords = {
        "count_total_exceptions": [
            "exception"
        ],
        "count_value_mismatches": [
            "mismatch",
            "value difference",
            "amount difference",
            "different values",
            "different amounts"
        ],
        "count_duplicate_entries": [
            "duplicate",
            "duplicates",
            "repeated entries"
        ],
        "count_missing_in_system_b": [
            "missing",
            "absent from system b",
            "not in system b"
        ],
        "count_unmatched_in_system_a": [
            "unmatched",
            "not in system a",
            "no matching record in system a"
        ]
    }

    keywords = intent_keywords.get(intent, [])

    return any(
        keyword in question
        for keyword in keywords
    )



def detect_intent(question: str):
    prompt = f"""
You are an intent classifier for a database reconciliation application.

Understand the user's question and return exactly one JSON object.

Allowed intents:
- count_total_exceptions
- count_value_mismatches
- count_duplicate_entries
- count_missing_in_system_b
- count_unmatched_in_system_a
- unsupported

Rules:
1. Return count_value_mismatches for questions about value mismatches.
2. Return count_duplicate_entries for questions about duplicate entries.
3. Return count_missing_in_system_b for records missing in System B.
4. Return count_unmatched_in_system_a for records unmatched in System A.
5. Return count_total_exceptions for questions about the total number of exceptions.
6. Return unsupported for anything else.
7. Do not calculate counts or invent database information.

User question: {question}

Expected JSON format:
{{"intent": "count_value_mismatches"}}
"""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            },
            timeout=60
        )

        response.raise_for_status()

        content = response.json()["message"]["content"]
        result = json.loads(content)

        intent = result.get("intent")

        if intent not in SUPPORTED_INTENTS:
            return None

        if not question_matches_intent(question, intent):
            return None

        return intent



    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
        TypeError
    ):
        return None


def answer_question(
    db: Session,
    organization_id: int,
    question: str
):
    # Step 1: Ask Ollama to understand the question.
    intent = detect_intent(question)

    # Step 2: Refuse unsupported or invalid questions.
    if intent is None:
        return {
            "answer": (
                "I cannot answer this question using the "
                "available reconciliation data."
            ),
            "grounded": False,
            "citations": []
        }

    # Step 3: Get the database query configuration.
    intent_config = SUPPORTED_INTENTS[intent]
    reason_code = intent_config["reason_code"]
    label = intent_config["label"]

    # Step 4: Query only the current organization's records.
    query = db.query(ReconciliationException).filter(
        ReconciliationException.organization_id == organization_id
    )

    if reason_code:
        query = query.filter(
            ReconciliationException.reason_code == reason_code
        )

    exceptions = query.order_by(
        ReconciliationException.id
    ).all()

    # Step 5: Build citations from actual database rows.
    citations = [
        {
            "exception_id": exception.id,
            "normalized_reference": exception.normalized_reference,
            "reason_code": exception.reason_code,
            "system_a_source_id": exception.system_a_source_id,
            "system_b_entry_ids": exception.system_b_entry_ids or []
        }
        for exception in exceptions
    ]

    # Step 6: Build an answer using database results only.
    if not exceptions:
        answer = (
            f"No {label} were found in this organization's "
            "reconciliation records."
        )
    else:
        count = len(exceptions)

        exception_ids = ", ".join(
            str(exception.id) for exception in exceptions
        )

        references = ", ".join(
            exception.normalized_reference
            for exception in exceptions
        )

        answer = (
            f"There are {count} {label}. "
            f"Supporting exception IDs: {exception_ids}. "
            f"Source references: {references}."
        )

    return {
        "answer": answer,
        "grounded": True,
        "citations": citations
    }
