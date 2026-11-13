
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.database import SessionLocal


def test_no_tenant_context_returns_no_locations():
    with SessionLocal() as db:
        result = db.execute(
            text("SELECT id FROM locations")
        )

        assert result.fetchall() == []


def test_organization_can_only_see_its_own_locations():
    with SessionLocal() as db:
        db.execute(
            text("SELECT set_config('app.current_org', :org_id, true)"),
            {"org_id": "1"}
        )

        result = db.execute(
            text("SELECT organization_id FROM locations")
        )

        organization_ids = {
            row.organization_id for row in result.fetchall()
        }

        assert organization_ids == {1}


def test_organization_cannot_insert_another_organizations_location():
    with SessionLocal() as db:
        db.execute(
            text("SELECT set_config('app.current_org', :org_id, true)"),
            {"org_id": "1"}
        )

        unique_code = f"TEST-{uuid.uuid4().hex[:8]}"

        with pytest.raises(DBAPIError) as error:
            db.execute(
                text("""
                    INSERT INTO locations
                    (location_code, name, organization_id)
                    VALUES (:code, :name, :org_id)
                """),
                {
                    "code": unique_code,
                    "name": "Unauthorized Test Location",
                    "org_id": 2
                }
            )

        db.rollback()

        assert getattr(error.value.orig, "sqlstate", None) == "42501"
