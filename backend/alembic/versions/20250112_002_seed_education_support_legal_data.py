"""seed_education_support_legal_data

Revision ID: 20250112_002_seed_education_support_legal_data
Revises: 20250112_001_add_education_support_legal_tables
Create Date: 2025-01-12 12:01:00.000000

Seed initial data cho Education, Support, và Legal modules
"""
from typing import Sequence, Union
from datetime import datetime, timedelta

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250112_002_seed_education_support_legal_data'
down_revision: Union[str, None] = '20250112_001_add_education_support_legal_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Seed initial data cho Education, Support, và Legal modules
    """
    
    # ========== Support Categories ==========
    categories_table = sa.table(
        'support_categories',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('slug', sa.String),
        sa.column('description', sa.Text),
        sa.column('is_active', sa.Boolean),
        sa.column('sort_order', sa.Integer),
    )
    
    op.bulk_insert(categories_table, [
        {'id': 1, 'name': 'Getting Started', 'slug': 'getting-started', 'description': 'Getting started guides', 'is_active': True, 'sort_order': 1},
        {'id': 2, 'name': 'Account Management', 'slug': 'account-management', 'description': 'Account and profile management', 'is_active': True, 'sort_order': 2},
        {'id': 3, 'name': 'Trading', 'slug': 'trading', 'description': 'Trading guides and tutorials', 'is_active': True, 'sort_order': 3},
        {'id': 4, 'name': 'Deposits & Withdrawals', 'slug': 'deposits-withdrawals', 'description': 'Deposit and withdrawal help', 'is_active': True, 'sort_order': 4},
        {'id': 5, 'name': 'Security', 'slug': 'security', 'description': 'Security and safety guides', 'is_active': True, 'sort_order': 5},
    ])
    
    # ========== Support Articles ==========
    articles_table = sa.table(
        'support_articles',
        sa.column('id', sa.Integer),
        sa.column('title', sa.String),
        sa.column('slug', sa.String),
        sa.column('content', sa.Text),
        sa.column('excerpt', sa.Text),
        sa.column('category_id', sa.Integer),
        sa.column('language', sa.String),
        sa.column('is_published', sa.Boolean),
        sa.column('is_featured', sa.Boolean),
        sa.column('sort_order', sa.Integer),
    )
    
    op.bulk_insert(articles_table, [
        {
            'id': 1,
            'title': 'How to Create an Account',
            'slug': 'how-to-create-an-account',
            'content': 'Step-by-step guide to creating your account...',
            'excerpt': 'Learn how to create your trading account in minutes',
            'category_id': 1,
            'language': 'en',
            'is_published': True,
            'is_featured': True,
            'sort_order': 1
        },
        {
            'id': 2,
            'title': 'How to Deposit Funds',
            'slug': 'how-to-deposit-funds',
            'content': 'Complete guide to depositing funds...',
            'excerpt': 'Learn how to deposit funds into your account',
            'category_id': 4,
            'language': 'en',
            'is_published': True,
            'is_featured': True,
            'sort_order': 1
        },
    ])
    
    # ========== Support Offices ==========
    offices_table = sa.table(
        'support_offices',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('address', sa.Text),
        sa.column('city', sa.String),
        sa.column('country', sa.String),
        sa.column('phone', sa.String),
        sa.column('email', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('is_headquarters', sa.Boolean),
        sa.column('sort_order', sa.Integer),
    )
    
    op.bulk_insert(offices_table, [
        {
            'id': 1,
            'name': 'Headquarters',
            'address': '123 Trading Street, Financial District',
            'city': 'New York',
            'country': 'United States',
            'phone': '+1-555-0123',
            'email': 'support@example.com',
            'is_active': True,
            'is_headquarters': True,
            'sort_order': 1
        },
    ])
    
    # ========== Support Channels ==========
    channels_table = sa.table(
        'support_channels',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('type', sa.String),
        sa.column('description', sa.Text),
        sa.column('value', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('is_primary', sa.Boolean),
        sa.column('sort_order', sa.Integer),
    )
    
    op.bulk_insert(channels_table, [
        {'id': 1, 'name': 'Email Support', 'type': 'email', 'description': 'Email support', 'value': 'support@example.com', 'is_active': True, 'is_primary': True, 'sort_order': 1},
        {'id': 2, 'name': 'Live Chat', 'type': 'chat', 'description': '24/7 live chat support', 'value': 'https://chat.example.com', 'is_active': True, 'is_primary': False, 'sort_order': 2},
        {'id': 3, 'name': 'Phone Support', 'type': 'phone', 'description': 'Phone support', 'value': '+1-555-0123', 'is_active': True, 'is_primary': False, 'sort_order': 3},
    ])
    
    # ========== FAQ ==========
    faq_table = sa.table(
        'faq',
        sa.column('id', sa.Integer),
        sa.column('question', sa.String),
        sa.column('answer', sa.Text),
        sa.column('category', sa.String),
        sa.column('language', sa.String),
        sa.column('is_published', sa.Boolean),
        sa.column('is_featured', sa.Boolean),
        sa.column('sort_order', sa.Integer),
    )
    
    op.bulk_insert(faq_table, [
        {
            'id': 1,
            'question': 'What is the minimum deposit amount?',
            'answer': 'The minimum deposit amount is $100 USD.',
            'category': 'deposits',
            'language': 'en',
            'is_published': True,
            'is_featured': True,
            'sort_order': 1
        },
        {
            'id': 2,
            'question': 'How long does withdrawal take?',
            'answer': 'Withdrawals are typically processed within 24-48 hours.',
            'category': 'withdrawals',
            'language': 'en',
            'is_published': True,
            'is_featured': True,
            'sort_order': 1
        },
        {
            'id': 3,
            'question': 'How do I verify my account?',
            'answer': 'You can verify your account by uploading required documents in the KYC section.',
            'category': 'account',
            'language': 'en',
            'is_published': True,
            'is_featured': False,
            'sort_order': 2
        },
    ])
    
    # ========== Terms of Service ==========
    terms_table = sa.table(
        'terms_of_service',
        sa.column('id', sa.Integer),
        sa.column('version', sa.String),
        sa.column('title', sa.String),
        sa.column('content', sa.Text),
        sa.column('effective_date', sa.DateTime),
        sa.column('is_active', sa.Boolean),
        sa.column('is_current', sa.Boolean),
    )
    
    op.bulk_insert(terms_table, [
        {
            'id': 1,
            'version': '1.0',
            'title': 'Terms of Service v1.0',
            'content': 'These Terms of Service govern your use of our platform...',
            'effective_date': datetime.utcnow() - timedelta(days=365),
            'is_active': True,
            'is_current': True
        },
    ])
    
    # ========== Privacy Policy ==========
    privacy_table = sa.table(
        'privacy_policy',
        sa.column('id', sa.Integer),
        sa.column('version', sa.String),
        sa.column('title', sa.String),
        sa.column('content', sa.Text),
        sa.column('effective_date', sa.DateTime),
        sa.column('is_active', sa.Boolean),
        sa.column('is_current', sa.Boolean),
    )
    
    op.bulk_insert(privacy_table, [
        {
            'id': 1,
            'version': '1.0',
            'title': 'Privacy Policy v1.0',
            'content': 'This Privacy Policy describes how we collect and use your information...',
            'effective_date': datetime.utcnow() - timedelta(days=365),
            'is_active': True,
            'is_current': True
        },
    ])
    
    # ========== Risk Warning ==========
    risk_warning_table = sa.table(
        'risk_warning',
        sa.column('id', sa.Integer),
        sa.column('title', sa.String),
        sa.column('content', sa.Text),
        sa.column('severity', sa.String),
        sa.column('language', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('is_current', sa.Boolean),
        sa.column('show_on_registration', sa.Boolean),
    )
    
    op.bulk_insert(risk_warning_table, [
        {
            'id': 1,
            'title': 'Trading Risk Warning',
            'content': 'Trading involves substantial risk of loss. Only trade with funds you can afford to lose...',
            'severity': 'high',
            'language': 'en',
            'is_active': True,
            'is_current': True,
            'show_on_registration': True
        },
    ])


def downgrade() -> None:
    """
    Xóa seed data
    """
    op.execute("DELETE FROM risk_warning WHERE id IN (1)")
    op.execute("DELETE FROM privacy_policy WHERE id IN (1)")
    op.execute("DELETE FROM terms_of_service WHERE id IN (1)")
    op.execute("DELETE FROM faq WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM support_channels WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM support_offices WHERE id IN (1)")
    op.execute("DELETE FROM support_articles WHERE id IN (1, 2)")
    op.execute("DELETE FROM support_categories WHERE id IN (1, 2, 3, 4, 5)")

