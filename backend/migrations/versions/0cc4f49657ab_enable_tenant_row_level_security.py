
from typing import Sequence, Union

from alembic import op


# Alembic migration identifiers
revision: str = "0cc4f49657ab"
down_revision: Union[str, Sequence[str], None] = "04b196484901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TENANT_TABLES = [
    "users",
    "locations",
    "system_a_records",
    "system_b_records",
    "reconciliation_exceptions",
]


def upgrade() -> None:

    for table in TENANT_TABLES:

        op.execute(f"""
            ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
            ALTER TABLE {table} FORCE ROW LEVEL SECURITY;

            CREATE POLICY tenant_isolation ON {table}
            USING (
                organization_id =
                NULLIF(
                    current_setting('app.current_org', true),
                    ''
                )::bigint
            )
            WITH CHECK (
                organization_id =
                NULLIF(
                    current_setting('app.current_org', true),
                    ''
                )::bigint
            );
        """)

    # Organizations uses id instead of organization_id.
    op.execute("""
        ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE organizations FORCE ROW LEVEL SECURITY;

        CREATE POLICY tenant_isolation ON organizations
        USING (
            id = NULLIF(
                current_setting('app.current_org', true),
                ''
            )::bigint
        )
        WITH CHECK (
            id = NULLIF(
                current_setting('app.current_org', true),
                ''
            )::bigint
        );
    """)


def downgrade() -> None:

    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation ON organizations;
        ALTER TABLE organizations NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
    """)

    for table in TENANT_TABLES:

        op.execute(f"""
            DROP POLICY IF EXISTS tenant_isolation ON {table};
            ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;
        """)
