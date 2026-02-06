"""add_sections_table

Revision ID: 5482f219c85c
Revises: 2772d4995944
Create Date: 2026-02-06 17:37:20.712262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5482f219c85c'
down_revision: Union[str, None] = '2772d4995944'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['sections.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_sections_parent_id', 'sections', ['parent_id'])
    op.create_index('ix_sections_order', 'sections', ['order'])
    op.create_index('ix_sections_is_active', 'sections', ['is_active'])


def downgrade() -> None:
    op.drop_index('ix_sections_is_active', table_name='sections')
    op.drop_index('ix_sections_order', table_name='sections')
    op.drop_index('ix_sections_parent_id', table_name='sections')
    op.drop_table('sections')
