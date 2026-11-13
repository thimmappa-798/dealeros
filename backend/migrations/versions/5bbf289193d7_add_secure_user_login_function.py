
from typing import Sequence, Union

from alembic import op


revision: str = "5bbf289193d7"
down_revision: Union[str, Sequence[str], None] = "0cc4f49657ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("""
        CREATE OR REPLACE FUNCTION public.authenticate_user(
            p_email TEXT,
            p_organization_code TEXT
        )
        RETURNS TABLE (
            user_id INTEGER,
            username VARCHAR(100),
            email VARCHAR(255),
            hashed_password VARCHAR(255),
            organization_id INTEGER
        )
        LANGUAGE SQL
        SECURITY DEFINER
        SET search_path = public, pg_temp
        AS $$
            SELECT
                u.id,
                u.username,
                u.email,
                u.hashed_password,
                u.organization_id
            FROM public.users AS u
            JOIN public.organizations AS o
                ON o.id = u.organization_id
            WHERE LOWER(u.email) = LOWER(p_email)
              AND o.external_id = p_organization_code
            LIMIT 1;
        $$;
    """)

    # Only the application role can execute this function.
    op.execute("""
        REVOKE ALL ON FUNCTION
        public.authenticate_user(TEXT, TEXT)
        FROM PUBLIC;
    """)

    op.execute("""
        GRANT EXECUTE ON FUNCTION
        public.authenticate_user(TEXT, TEXT)
        TO dealeros_app;
    """)


def downgrade() -> None:

    op.execute("""
        DROP FUNCTION IF EXISTS
        public.authenticate_user(TEXT, TEXT);
    """)
