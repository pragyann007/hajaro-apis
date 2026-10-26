"""initial_clean_schema

Revision ID: ef7499257c98
Revises: 
Create Date: 2026-10-26 18:13:00.820046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = 'ef7499257c98'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE SCHEMA IF NOT EXISTS hajaro;')
    
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name_en', sa.String(length=150), nullable=False),
    sa.Column('name_ne', sa.String(length=150), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    op.create_index(op.f('ix_hajaro_categories_name_en'), 'categories', ['name_en'], unique=False, schema='hajaro')
    op.create_index(op.f('ix_hajaro_categories_name_ne'), 'categories', ['name_ne'], unique=False, schema='hajaro')
    op.create_index(op.f('ix_hajaro_categories_slug'), 'categories', ['slug'], unique=True, schema='hajaro')
    
    op.create_table('locations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name_en', sa.String(length=150), nullable=False),
    sa.Column('name_ne', sa.String(length=150), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('location_type', sa.Enum('PROVINCE', 'DISTRICT', 'MUNICIPALITY', 'WARD', 'CITY', 'LOCALITY', 'BAZAAR', 'CHOWK', 'ROAD', 'LANDMARK', name='locationtype'), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['hajaro.locations.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    op.create_index(op.f('ix_hajaro_locations_name_en'), 'locations', ['name_en'], unique=False, schema='hajaro')
    op.create_index(op.f('ix_hajaro_locations_name_ne'), 'locations', ['name_ne'], unique=False, schema='hajaro')
    op.create_index(op.f('ix_hajaro_locations_slug'), 'locations', ['slug'], unique=True, schema='hajaro')
    
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('profile_url', sa.String(length=2083), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    op.create_index(op.f('ix_hajaro_users_email'), 'users', ['email'], unique=True, schema='hajaro')
    
    op.create_table('businesses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('phone', sa.String(length=30), nullable=True),
    sa.Column('whatsapp', sa.String(length=30), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('website', sa.String(length=255), nullable=True),
    sa.Column('address_line', sa.String(length=255), nullable=True),
    sa.Column('ownerId', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('geographic_point', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, dimension=2, from_text='ST_GeogFromText', name='geography', nullable=False), nullable=False),
    sa.Column('publication_status', sa.Enum('draft', 'pending_review', 'published', 'rejected', 'suspended', name='publicationstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['hajaro.locations.id'], ),
    sa.ForeignKeyConstraint(['ownerId'], ['hajaro.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    op.create_index(op.f('ix_hajaro_businesses_name'), 'businesses', ['name'], unique=False, schema='hajaro')
    op.create_index(op.f('ix_hajaro_businesses_slug'), 'businesses', ['slug'], unique=True, schema='hajaro')
    
    op.create_table('business_categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['hajaro.businesses.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['hajaro.categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    
    op.create_table('business_claims',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('applicant_reference', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='status', schema='hajaro'), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['hajaro.businesses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    op.create_index(op.f('ix_hajaro_business_claims_status'), 'business_claims', ['status'], unique=False, schema='hajaro')
    op.create_index('uq_one_pending_claim_per_business', 'business_claims', ['business_id'], unique=True, schema='hajaro', postgresql_where="status = 'PENDING'")
    
    op.create_table('business_hours',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('weekday', sa.Integer(), nullable=False),
    sa.Column('open_time', sa.Time(timezone=True), nullable=False),
    sa.Column('close_time', sa.Time(timezone=True), nullable=False),
    sa.Column('is_closed', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['hajaro.businesses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    
    op.create_table('business_media',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('file_url', sa.String(length=2083), nullable=False),
    sa.Column('media_type', sa.Enum('IMAGE', 'VIDEO', 'PDF', name='mediatype', schema='hajaro'), nullable=False),
    sa.Column('alt_text', sa.String(), nullable=True),
    sa.Column('is_cover', sa.Boolean(), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['hajaro.businesses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='hajaro'
    )
    op.create_index('uq_business_cover_image', 'business_media', ['business_id'], unique=True, schema='hajaro', postgresql_where='is_cover = true')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_business_cover_image', table_name='business_media', schema='hajaro')
    op.drop_table('business_media', schema='hajaro')
    op.drop_table('business_hours', schema='hajaro')
    op.drop_index('uq_one_pending_claim_per_business', table_name='business_claims', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_business_claims_status'), table_name='business_claims', schema='hajaro')
    op.drop_table('business_claims', schema='hajaro')
    op.drop_table('business_categories', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_businesses_slug'), table_name='businesses', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_businesses_name'), table_name='businesses', schema='hajaro')
    op.drop_table('businesses', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_users_email'), table_name='users', schema='hajaro')
    op.drop_table('users', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_locations_slug'), table_name='locations', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_locations_name_ne'), table_name='locations', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_locations_name_en'), table_name='locations', schema='hajaro')
    op.drop_table('locations', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_categories_slug'), table_name='categories', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_categories_name_ne'), table_name='categories', schema='hajaro')
    op.drop_index(op.f('ix_hajaro_categories_name_en'), table_name='categories', schema='hajaro')
    op.drop_table('categories', schema='hajaro')
