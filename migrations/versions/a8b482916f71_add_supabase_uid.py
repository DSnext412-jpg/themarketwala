"""add supabase_uid to users

Revision ID: a8b482916f71
Revises: e40e5a96887e
Create Date: 2026-06-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a8b482916f71'
down_revision = 'e40e5a96887e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('supabase_uid', sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, 'users', ['supabase_uid'])


def downgrade():
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'supabase_uid')
