"""Phase 1 - Core tables: users, text_entries, settings

Revision ID: 002_phase1_core
Revises: 001_initial
Create Date: 2024-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_phase1_core"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('user', 'moderator', 'admin');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255),
            username VARCHAR(255),
            role user_role NOT NULL DEFAULT 'user',
            is_blocked BOOLEAN NOT NULL DEFAULT false,
            language VARCHAR(10) NOT NULL DEFAULT 'ar',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_active_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS text_entries (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) NOT NULL,
            language VARCHAR(10) NOT NULL DEFAULT 'ar',
            text TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            CONSTRAINT uq_text_key_language UNIQUE (key, language)
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_text_entries_key ON text_entries (key);")

    op.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) NOT NULL UNIQUE,
            value TEXT NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_settings_key ON settings (key);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS settings;")
    op.execute("DROP TABLE IF EXISTS text_entries;")
    op.execute("DROP TABLE IF EXISTS users;")
    op.execute("DROP TYPE IF EXISTS user_role;")
