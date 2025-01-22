"""Add channel_statuses and message_statuses

Revision ID: 858ef6be78a4
Revises: f8aaddc28a9e
Create Date: 2025-01-22 14:56:18.558213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '858ef6be78a4'
down_revision: Union[str, None] = 'f8aaddc28a9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('created', 'delivered', 'enriched', 'failed', 'pending_enrichment', 'sending', name='messagestatuses').create(op.get_bind())
    sa.Enum('delivered', 'notification_attempted', 'notified', 'permanent_failure', 'read', 'received', 'rejected', 'technical_failure', 'temporary_failure', 'unnotified', name='channelstatuses').create(op.get_bind())
    op.create_table('channel_statuses',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('message_reference', sa.UUID(), nullable=False),
    sa.Column('status', postgresql.ENUM('delivered', 'notification_attempted', 'notified', 'permanent_failure', 'read', 'received', 'rejected', 'technical_failure', 'temporary_failure', 'unnotified', name='channelstatuses', create_type=False), nullable=True),
    sa.PrimaryKeyConstraint('idempotency_key')
    )
    op.create_table('message_statuses',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('message_reference', sa.UUID(), nullable=False),
    sa.Column('status', postgresql.ENUM('created', 'delivered', 'enriched', 'failed', 'pending_enrichment', 'sending', name='messagestatuses', create_type=False), nullable=True),
    sa.PrimaryKeyConstraint('idempotency_key')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_statuses')
    op.drop_table('channel_statuses')
    sa.Enum('delivered', 'notification_attempted', 'notified', 'permanent_failure', 'read', 'received', 'rejected', 'technical_failure', 'temporary_failure', 'unnotified', name='channelstatuses').drop(op.get_bind())
    sa.Enum('created', 'delivered', 'enriched', 'failed', 'pending_enrichment', 'sending', name='messagestatuses').drop(op.get_bind())
    # ### end Alembic commands ###