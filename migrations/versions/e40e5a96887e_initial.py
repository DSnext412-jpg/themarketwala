"""initial

Revision ID: e40e5a96887e
Revises:
Create Date: 2026-06-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e40e5a96887e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('interests', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table('courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=250), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.String(length=50), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('reading_time', sa.String(length=50), nullable=True),
        sa.Column('lecture_times', sa.Text(), nullable=True),
        sa.Column('drive_link', sa.String(length=500), nullable=True),
        sa.Column('live_meeting_link', sa.String(length=500), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table('blogs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=250), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('featured_image', sa.String(length=500), nullable=True),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('seo_title', sa.String(length=200), nullable=True),
        sa.Column('seo_description', sa.String(length=300), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table('purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('customer_name', sa.String(length=100), nullable=True),
        sa.Column('customer_email', sa.String(length=120), nullable=True),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('profession', sa.String(length=100), nullable=True),
        sa.Column('experience', sa.String(length=50), nullable=True),
        sa.Column('payment_id', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('purchased_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'course_id')
    )
    op.create_table('progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'course_id')
    )


def downgrade():
    op.drop_table('progress')
    op.drop_table('bookmarks')
    op.drop_table('notifications')
    op.drop_table('purchases')
    op.drop_table('blogs')
    op.drop_table('courses')
    op.drop_table('users')
