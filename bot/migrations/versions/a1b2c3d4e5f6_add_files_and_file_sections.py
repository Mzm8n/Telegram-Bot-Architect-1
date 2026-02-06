"""add_files_and_file_sections_tables

Revision ID: a1b2c3d4e5f6
Revises: 5482f219c85c
Create Date: 2026-02-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5482f219c85c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'files',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('file_id', sa.String(255), nullable=False),
        sa.Column('file_unique_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('size', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='published'),
        sa.Column('uploaded_by', sa.BigInteger(), nullable=False),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_files_file_id', 'files', ['file_id'])
    op.create_index('ix_files_file_unique_id', 'files', ['file_unique_id'], unique=True)
    op.create_index('ix_files_uploaded_by', 'files', ['uploaded_by'])
    op.create_index('ix_files_status', 'files', ['status'])
    op.create_index('ix_files_is_active', 'files', ['is_active'])

    op.create_table(
        'file_sections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('file_id', sa.BigInteger(), nullable=False),
        sa.Column('section_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_file_sections_file_id', 'file_sections', ['file_id'])
    op.create_index('ix_file_sections_section_id', 'file_sections', ['section_id'])
    op.create_unique_constraint('uq_file_section', 'file_sections', ['file_id', 'section_id'])


def downgrade() -> None:
    op.drop_constraint('uq_file_section', 'file_sections', type_='unique')
    op.drop_index('ix_file_sections_section_id', table_name='file_sections')
    op.drop_index('ix_file_sections_file_id', table_name='file_sections')
    op.drop_table('file_sections')

    op.drop_index('ix_files_is_active', table_name='files')
    op.drop_index('ix_files_status', table_name='files')
    op.drop_index('ix_files_uploaded_by', table_name='files')
    op.drop_index('ix_files_file_unique_id', table_name='files')
    op.drop_index('ix_files_file_id', table_name='files')
    op.drop_table('files')
