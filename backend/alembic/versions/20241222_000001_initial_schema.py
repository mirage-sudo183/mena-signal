"""Initial schema

Revision ID: 20241222_000001
Revises: 
Create Date: 2024-12-22 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20241222_000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('rss', 'api', 'manual', name='sourcetype'), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('type', sa.Enum('funding', 'company', name='itemtype'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('raw_json', sa.JSON(), nullable=True),
        sa.Column('hash', sa.String(length=64), nullable=False),
        sa.Column('hidden', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_items_hash', 'items', ['hash'], unique=True)
    op.create_index('ix_items_type_published', 'items', ['type', 'published_at'])
    op.create_index('ix_items_company_name', 'items', ['company_name'])

    # Create funding_details table
    op.create_table(
        'funding_details',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('round_type', sa.String(length=50), nullable=True),
        sa.Column('amount_usd', sa.Float(), nullable=True),
        sa.Column('investors', sa.JSON(), nullable=True),
        sa.Column('geography', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )

    # Create company_details table
    op.create_table(
        'company_details',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('one_liner', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('stage_hint', sa.String(length=50), nullable=True),
        sa.Column('geography', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )

    # Create mena_analysis table
    op.create_table(
        'mena_analysis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('fit_score', sa.Integer(), nullable=False),
        sa.Column('mena_summary', sa.Text(), nullable=False),
        sa.Column('rubric_json', sa.JSON(), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create favorites table
    op.create_table(
        'favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_favorites_user_item', 'favorites', ['user_id', 'item_id'], unique=True)

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tags_user_name', 'tags', ['user_id', 'name'], unique=True)

    # Create item_tags table
    op.create_table(
        'item_tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_item_tags_item_tag', 'item_tags', ['item_id', 'tag_id'], unique=True)

    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create ingest_runs table
    op.create_table(
        'ingest_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('running', 'success', 'failed', name='ingeststatus'), nullable=True),
        sa.Column('items_added', sa.Integer(), nullable=True, default=0),
        sa.Column('error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('ingest_runs')
    op.drop_table('notes')
    op.drop_index('ix_item_tags_item_tag', table_name='item_tags')
    op.drop_table('item_tags')
    op.drop_index('ix_tags_user_name', table_name='tags')
    op.drop_table('tags')
    op.drop_index('ix_favorites_user_item', table_name='favorites')
    op.drop_table('favorites')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('mena_analysis')
    op.drop_table('company_details')
    op.drop_table('funding_details')
    op.drop_index('ix_items_company_name', table_name='items')
    op.drop_index('ix_items_type_published', table_name='items')
    op.drop_index('ix_items_hash', table_name='items')
    op.drop_table('items')
    op.drop_table('sources')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS sourcetype')
    op.execute('DROP TYPE IF EXISTS itemtype')
    op.execute('DROP TYPE IF EXISTS ingeststatus')

