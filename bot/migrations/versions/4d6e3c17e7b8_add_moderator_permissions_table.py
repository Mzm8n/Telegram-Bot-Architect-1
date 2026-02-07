"""add moderator_permissions table

Revision ID: 4d6e3c17e7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-02-07 17:14:07.392671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4d6e3c17e7b8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'moderator_permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('can_upload', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('can_link', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('can_publish', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('own_files_only', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_moderator_permissions_user_id'), 'moderator_permissions', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_moderator_permissions_user_id'), table_name='moderator_permissions')
    op.drop_table('moderator_permissions')
