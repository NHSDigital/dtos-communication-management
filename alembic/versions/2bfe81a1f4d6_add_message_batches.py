"""Add message_batches

Revision ID: 2bfe81a1f4d6
Revises:
Create Date: 2025-01-22 14:47:47.437252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2bfe81a1f4d6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('failed', 'not_sent', 'sent', name='messagebatchstatuses').create(op.get_bind())
    op.create_table('message_batches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('batch_id', sa.String(), nullable=True),
    sa.Column('batch_reference', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', postgresql.ENUM('failed', 'not_sent', 'sent', name='messagebatchstatuses', create_type=False), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_batches')
    sa.Enum('failed', 'not_sent', 'sent', name='messagebatchstatuses').drop(op.get_bind())
    # ### end Alembic commands ###
