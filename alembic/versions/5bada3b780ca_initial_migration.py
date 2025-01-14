"""Initial migration

Revision ID: 5bada3b780ca
Revises: 
Create Date: 2025-01-10 08:28:37.217487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bada3b780ca'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('batch_messages',
    sa.Column('batch_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('message_reference', sa.UUID(), nullable=False),
    sa.Column('nhs_number', sa.Text(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('NOT_SENT', 'SENT', 'FAILED', name='batchmessagestatus'), nullable=False),
    sa.PrimaryKeyConstraint('batch_id', 'message_reference', 'status')
    )
    op.create_table('channel_statuses',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('message_reference', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('DELIVERED', 'READ', 'NOTIFICATION_ATTEMPTED', 'UNNOTIFIED', 'REJECTED', 'NOTIFIED', 'RECEIVED', 'PERMANENT_FAILURE', 'TEMPORARY_FAILURE', 'TECHNICAL_FAILURE', name='channelstatus'), nullable=True),
    sa.PrimaryKeyConstraint('idempotency_key')
    )
    op.create_table('message_statuses',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('message_reference', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PENDING_ENRICHMENT', 'ENRICHED', 'SENDING', 'DELIVERED', 'FAILED', name='messagestatus'), nullable=True),
    sa.PrimaryKeyConstraint('idempotency_key')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_statuses')
    op.drop_table('channel_statuses')
    op.drop_table('batch_messages')
    # ### end Alembic commands ###
