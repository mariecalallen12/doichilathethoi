"""add_education_support_legal_tables

Revision ID: 20250112_001_add_education_support_legal_tables
Revises: 20250111_001_remove_trading_tables
Create Date: 2025-01-12 12:00:00.000000

Migration để tạo các bảng cho Education, Support, và Legal modules
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250112_001_add_education_support_legal_tables'
down_revision: Union[str, None] = '20250111_001_remove_trading_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Tạo các bảng cho Education, Support, và Legal modules
    """
    
    # ========== Education Tables ==========
    
    # Create education_videos table
    op.create_table(
        'education_videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('likes_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_education_videos_title'), 'education_videos', ['title'], unique=False)
    op.create_index(op.f('ix_education_videos_category'), 'education_videos', ['category'], unique=False)
    op.create_index(op.f('ix_education_videos_language'), 'education_videos', ['language'], unique=False)
    op.create_index(op.f('ix_education_videos_is_published'), 'education_videos', ['is_published'], unique=False)
    op.create_index(op.f('ix_education_videos_is_featured'), 'education_videos', ['is_featured'], unique=False)
    
    # Create education_ebooks table
    op.create_table(
        'education_ebooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cover_url', sa.String(length=500), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.Column('isbn', sa.String(length=50), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_education_ebooks_title'), 'education_ebooks', ['title'], unique=False)
    op.create_index(op.f('ix_education_ebooks_category'), 'education_ebooks', ['category'], unique=False)
    op.create_index(op.f('ix_education_ebooks_language'), 'education_ebooks', ['language'], unique=False)
    op.create_index(op.f('ix_education_ebooks_is_published'), 'education_ebooks', ['is_published'], unique=False)
    op.create_index(op.f('ix_education_ebooks_is_featured'), 'education_ebooks', ['is_featured'], unique=False)
    
    # Create economic_calendar table
    op.create_table(
        'economic_calendar',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'),
        sa.Column('impact', sa.String(length=20), nullable=True),
        sa.Column('previous_value', sa.String(length=100), nullable=True),
        sa.Column('forecast_value', sa.String(length=100), nullable=True),
        sa.Column('actual_value', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_economic_calendar_title'), 'economic_calendar', ['title'], unique=False)
    op.create_index(op.f('ix_economic_calendar_country'), 'economic_calendar', ['country'], unique=False)
    op.create_index(op.f('ix_economic_calendar_currency'), 'economic_calendar', ['currency'], unique=False)
    op.create_index(op.f('ix_economic_calendar_event_date'), 'economic_calendar', ['event_date'], unique=False)
    op.create_index(op.f('ix_economic_calendar_impact'), 'economic_calendar', ['impact'], unique=False)
    op.create_index('idx_economic_calendar_date_country', 'economic_calendar', ['event_date', 'country'], unique=False)
    
    # Create market_reports table
    op.create_table(
        'market_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('cover_url', sa.String(length=500), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('report_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('download_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_reports_title'), 'market_reports', ['title'], unique=False)
    op.create_index(op.f('ix_market_reports_category'), 'market_reports', ['category'], unique=False)
    op.create_index(op.f('ix_market_reports_language'), 'market_reports', ['language'], unique=False)
    op.create_index(op.f('ix_market_reports_report_date'), 'market_reports', ['report_date'], unique=False)
    op.create_index(op.f('ix_market_reports_is_published'), 'market_reports', ['is_published'], unique=False)
    op.create_index(op.f('ix_market_reports_is_featured'), 'market_reports', ['is_featured'], unique=False)
    
    # Create education_progress table
    op.create_table(
        'education_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('progress_percent', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0.00'),
        sa.Column('time_spent', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_position', sa.String(length=100), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_education_progress_user_id'), 'education_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_education_progress_item_type'), 'education_progress', ['item_type'], unique=False)
    op.create_index(op.f('ix_education_progress_item_id'), 'education_progress', ['item_id'], unique=False)
    op.create_index(op.f('ix_education_progress_is_completed'), 'education_progress', ['is_completed'], unique=False)
    op.create_index('idx_education_progress_user_item', 'education_progress', ['user_id', 'item_type', 'item_id'], unique=False)
    
    # ========== Support Tables ==========
    
    # Create support_categories table
    op.create_table(
        'support_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['support_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_support_categories_name'), 'support_categories', ['name'], unique=True)
    op.create_index(op.f('ix_support_categories_slug'), 'support_categories', ['slug'], unique=True)
    op.create_index(op.f('ix_support_categories_parent_id'), 'support_categories', ['parent_id'], unique=False)
    op.create_index(op.f('ix_support_categories_is_active'), 'support_categories', ['is_active'], unique=False)
    
    # Create support_articles table
    op.create_table(
        'support_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('not_helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('meta_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('related_article_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['support_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_support_articles_title'), 'support_articles', ['title'], unique=False)
    op.create_index(op.f('ix_support_articles_slug'), 'support_articles', ['slug'], unique=True)
    op.create_index(op.f('ix_support_articles_category_id'), 'support_articles', ['category_id'], unique=False)
    op.create_index(op.f('ix_support_articles_language'), 'support_articles', ['language'], unique=False)
    op.create_index(op.f('ix_support_articles_is_published'), 'support_articles', ['is_published'], unique=False)
    op.create_index(op.f('ix_support_articles_is_featured'), 'support_articles', ['is_featured'], unique=False)
    op.create_index(op.f('ix_support_articles_is_pinned'), 'support_articles', ['is_pinned'], unique=False)
    
    # Create support_contacts table
    op.create_table(
        'support_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('contact_type', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='normal'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('responded_by', sa.Integer(), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['responded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_contacts_user_id'), 'support_contacts', ['user_id'], unique=False)
    op.create_index(op.f('ix_support_contacts_email'), 'support_contacts', ['email'], unique=False)
    op.create_index(op.f('ix_support_contacts_subject'), 'support_contacts', ['subject'], unique=False)
    op.create_index(op.f('ix_support_contacts_contact_type'), 'support_contacts', ['contact_type'], unique=False)
    op.create_index(op.f('ix_support_contacts_priority'), 'support_contacts', ['priority'], unique=False)
    op.create_index(op.f('ix_support_contacts_status'), 'support_contacts', ['status'], unique=False)
    
    # Create support_offices table
    op.create_table(
        'support_offices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.String(length=50), nullable=True),
        sa.Column('longitude', sa.String(length=50), nullable=True),
        sa.Column('business_hours', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_headquarters', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_offices_name'), 'support_offices', ['name'], unique=False)
    op.create_index(op.f('ix_support_offices_city'), 'support_offices', ['city'], unique=False)
    op.create_index(op.f('ix_support_offices_country'), 'support_offices', ['country'], unique=False)
    op.create_index(op.f('ix_support_offices_is_active'), 'support_offices', ['is_active'], unique=False)
    op.create_index(op.f('ix_support_offices_is_headquarters'), 'support_offices', ['is_headquarters'], unique=False)
    
    # Create support_channels table
    op.create_table(
        'support_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('availability', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_primary', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('average_response_time', sa.String(length=50), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_support_channels_name'), 'support_channels', ['name'], unique=True)
    op.create_index(op.f('ix_support_channels_type'), 'support_channels', ['type'], unique=False)
    op.create_index(op.f('ix_support_channels_is_active'), 'support_channels', ['is_active'], unique=False)
    op.create_index(op.f('ix_support_channels_is_primary'), 'support_channels', ['is_primary'], unique=False)
    
    # Create faq table
    op.create_table(
        'faq',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('not_helpful_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('related_faq_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_faq_question'), 'faq', ['question'], unique=False)
    op.create_index(op.f('ix_faq_category'), 'faq', ['category'], unique=False)
    op.create_index(op.f('ix_faq_language'), 'faq', ['language'], unique=False)
    op.create_index(op.f('ix_faq_is_published'), 'faq', ['is_published'], unique=False)
    op.create_index(op.f('ix_faq_is_featured'), 'faq', ['is_featured'], unique=False)
    
    # ========== Legal Tables ==========
    
    # Create terms_of_service table
    op.create_table(
        'terms_of_service',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('changes_summary', sa.Text(), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version')
    )
    op.create_index(op.f('ix_terms_of_service_version'), 'terms_of_service', ['version'], unique=True)
    op.create_index(op.f('ix_terms_of_service_effective_date'), 'terms_of_service', ['effective_date'], unique=False)
    op.create_index(op.f('ix_terms_of_service_is_active'), 'terms_of_service', ['is_active'], unique=False)
    op.create_index(op.f('ix_terms_of_service_is_current'), 'terms_of_service', ['is_current'], unique=False)
    
    # Create privacy_policy table
    op.create_table(
        'privacy_policy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('changes_summary', sa.Text(), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version')
    )
    op.create_index(op.f('ix_privacy_policy_version'), 'privacy_policy', ['version'], unique=True)
    op.create_index(op.f('ix_privacy_policy_effective_date'), 'privacy_policy', ['effective_date'], unique=False)
    op.create_index(op.f('ix_privacy_policy_is_active'), 'privacy_policy', ['is_active'], unique=False)
    op.create_index(op.f('ix_privacy_policy_is_current'), 'privacy_policy', ['is_current'], unique=False)
    
    # Create risk_warning table
    op.create_table(
        'risk_warning',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True, server_default='high'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('show_on_registration', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('show_on_trading', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('require_acknowledgment', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_warning_category'), 'risk_warning', ['category'], unique=False)
    op.create_index(op.f('ix_risk_warning_severity'), 'risk_warning', ['severity'], unique=False)
    op.create_index(op.f('ix_risk_warning_language'), 'risk_warning', ['language'], unique=False)
    op.create_index(op.f('ix_risk_warning_is_active'), 'risk_warning', ['is_active'], unique=False)
    op.create_index(op.f('ix_risk_warning_is_current'), 'risk_warning', ['is_current'], unique=False)
    
    # Create complaints table
    op.create_table(
        'complaints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('complaint_type', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('related_transaction_id', sa.Integer(), nullable=True),
        sa.Column('related_order_id', sa.Integer(), nullable=True),
        sa.Column('related_reference', sa.String(length=255), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='normal'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='submitted'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('user_satisfaction', sa.String(length=20), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_user_id'), 'complaints', ['user_id'], unique=False)
    op.create_index(op.f('ix_complaints_complaint_type'), 'complaints', ['complaint_type'], unique=False)
    op.create_index(op.f('ix_complaints_subject'), 'complaints', ['subject'], unique=False)
    op.create_index(op.f('ix_complaints_priority'), 'complaints', ['priority'], unique=False)
    op.create_index(op.f('ix_complaints_status'), 'complaints', ['status'], unique=False)
    op.create_index(op.f('ix_complaints_submitted_at'), 'complaints', ['submitted_at'], unique=False)
    op.create_index(op.f('ix_complaints_assigned_to'), 'complaints', ['assigned_to'], unique=False)
    op.create_index('idx_complaints_user_status', 'complaints', ['user_id', 'status'], unique=False)
    op.create_index('idx_complaints_type_status', 'complaints', ['complaint_type', 'status'], unique=False)


def downgrade() -> None:
    """
    Xóa các bảng Education, Support, và Legal
    """
    # Drop indexes first
    op.drop_index('idx_complaints_type_status', table_name='complaints')
    op.drop_index('idx_complaints_user_status', table_name='complaints')
    op.drop_index(op.f('ix_complaints_assigned_to'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_submitted_at'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_status'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_priority'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_subject'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_complaint_type'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_user_id'), table_name='complaints')
    op.drop_table('complaints')
    
    op.drop_index(op.f('ix_risk_warning_is_current'), table_name='risk_warning')
    op.drop_index(op.f('ix_risk_warning_is_active'), table_name='risk_warning')
    op.drop_index(op.f('ix_risk_warning_language'), table_name='risk_warning')
    op.drop_index(op.f('ix_risk_warning_severity'), table_name='risk_warning')
    op.drop_index(op.f('ix_risk_warning_category'), table_name='risk_warning')
    op.drop_table('risk_warning')
    
    op.drop_index(op.f('ix_privacy_policy_is_current'), table_name='privacy_policy')
    op.drop_index(op.f('ix_privacy_policy_is_active'), table_name='privacy_policy')
    op.drop_index(op.f('ix_privacy_policy_effective_date'), table_name='privacy_policy')
    op.drop_index(op.f('ix_privacy_policy_version'), table_name='privacy_policy')
    op.drop_table('privacy_policy')
    
    op.drop_index(op.f('ix_terms_of_service_is_current'), table_name='terms_of_service')
    op.drop_index(op.f('ix_terms_of_service_is_active'), table_name='terms_of_service')
    op.drop_index(op.f('ix_terms_of_service_effective_date'), table_name='terms_of_service')
    op.drop_index(op.f('ix_terms_of_service_version'), table_name='terms_of_service')
    op.drop_table('terms_of_service')
    
    op.drop_index(op.f('ix_faq_is_featured'), table_name='faq')
    op.drop_index(op.f('ix_faq_is_published'), table_name='faq')
    op.drop_index(op.f('ix_faq_language'), table_name='faq')
    op.drop_index(op.f('ix_faq_category'), table_name='faq')
    op.drop_index(op.f('ix_faq_question'), table_name='faq')
    op.drop_table('faq')
    
    op.drop_index(op.f('ix_support_channels_is_primary'), table_name='support_channels')
    op.drop_index(op.f('ix_support_channels_is_active'), table_name='support_channels')
    op.drop_index(op.f('ix_support_channels_type'), table_name='support_channels')
    op.drop_index(op.f('ix_support_channels_name'), table_name='support_channels')
    op.drop_table('support_channels')
    
    op.drop_index(op.f('ix_support_offices_is_headquarters'), table_name='support_offices')
    op.drop_index(op.f('ix_support_offices_is_active'), table_name='support_offices')
    op.drop_index(op.f('ix_support_offices_country'), table_name='support_offices')
    op.drop_index(op.f('ix_support_offices_city'), table_name='support_offices')
    op.drop_index(op.f('ix_support_offices_name'), table_name='support_offices')
    op.drop_table('support_offices')
    
    op.drop_index(op.f('ix_support_contacts_status'), table_name='support_contacts')
    op.drop_index(op.f('ix_support_contacts_priority'), table_name='support_contacts')
    op.drop_index(op.f('ix_support_contacts_contact_type'), table_name='support_contacts')
    op.drop_index(op.f('ix_support_contacts_subject'), table_name='support_contacts')
    op.drop_index(op.f('ix_support_contacts_email'), table_name='support_contacts')
    op.drop_index(op.f('ix_support_contacts_user_id'), table_name='support_contacts')
    op.drop_table('support_contacts')
    
    op.drop_index(op.f('ix_support_articles_is_pinned'), table_name='support_articles')
    op.drop_index(op.f('ix_support_articles_is_featured'), table_name='support_articles')
    op.drop_index(op.f('ix_support_articles_is_published'), table_name='support_articles')
    op.drop_index(op.f('ix_support_articles_language'), table_name='support_articles')
    op.drop_index(op.f('ix_support_articles_category_id'), table_name='support_articles')
    op.drop_index(op.f('ix_support_articles_slug'), table_name='support_articles')
    op.drop_index(op.f('ix_support_articles_title'), table_name='support_articles')
    op.drop_table('support_articles')
    
    op.drop_index(op.f('ix_support_categories_is_active'), table_name='support_categories')
    op.drop_index(op.f('ix_support_categories_parent_id'), table_name='support_categories')
    op.drop_index(op.f('ix_support_categories_slug'), table_name='support_categories')
    op.drop_index(op.f('ix_support_categories_name'), table_name='support_categories')
    op.drop_table('support_categories')
    
    op.drop_index('idx_education_progress_user_item', table_name='education_progress')
    op.drop_index(op.f('ix_education_progress_is_completed'), table_name='education_progress')
    op.drop_index(op.f('ix_education_progress_item_id'), table_name='education_progress')
    op.drop_index(op.f('ix_education_progress_item_type'), table_name='education_progress')
    op.drop_index(op.f('ix_education_progress_user_id'), table_name='education_progress')
    op.drop_table('education_progress')
    
    op.drop_index(op.f('ix_market_reports_is_featured'), table_name='market_reports')
    op.drop_index(op.f('ix_market_reports_is_published'), table_name='market_reports')
    op.drop_index(op.f('ix_market_reports_report_date'), table_name='market_reports')
    op.drop_index(op.f('ix_market_reports_language'), table_name='market_reports')
    op.drop_index(op.f('ix_market_reports_category'), table_name='market_reports')
    op.drop_index(op.f('ix_market_reports_title'), table_name='market_reports')
    op.drop_table('market_reports')
    
    op.drop_index('idx_economic_calendar_date_country', table_name='economic_calendar')
    op.drop_index(op.f('ix_economic_calendar_impact'), table_name='economic_calendar')
    op.drop_index(op.f('ix_economic_calendar_event_date'), table_name='economic_calendar')
    op.drop_index(op.f('ix_economic_calendar_currency'), table_name='economic_calendar')
    op.drop_index(op.f('ix_economic_calendar_country'), table_name='economic_calendar')
    op.drop_index(op.f('ix_economic_calendar_title'), table_name='economic_calendar')
    op.drop_table('economic_calendar')
    
    op.drop_index(op.f('ix_education_ebooks_is_featured'), table_name='education_ebooks')
    op.drop_index(op.f('ix_education_ebooks_is_published'), table_name='education_ebooks')
    op.drop_index(op.f('ix_education_ebooks_language'), table_name='education_ebooks')
    op.drop_index(op.f('ix_education_ebooks_category'), table_name='education_ebooks')
    op.drop_index(op.f('ix_education_ebooks_title'), table_name='education_ebooks')
    op.drop_table('education_ebooks')
    
    op.drop_index(op.f('ix_education_videos_is_featured'), table_name='education_videos')
    op.drop_index(op.f('ix_education_videos_is_published'), table_name='education_videos')
    op.drop_index(op.f('ix_education_videos_language'), table_name='education_videos')
    op.drop_index(op.f('ix_education_videos_category'), table_name='education_videos')
    op.drop_index(op.f('ix_education_videos_title'), table_name='education_videos')
    op.drop_table('education_videos')

