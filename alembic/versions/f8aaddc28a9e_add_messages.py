"""Add messages

Revision ID: f8aaddc28a9e
Revises: 2bfe81a1f4d6
Create Date: 2025-01-22 14:48:13.189762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f8aaddc28a9e'
down_revision: Union[str, None] = '2bfe81a1f4d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('batch_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('message_id', sa.String(), nullable=False),
    sa.Column('message_reference', sa.UUID(), nullable=False),
    sa.Column('nhs_number', sa.Text(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['batch_id'], ['message_batches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('messages')
    # ### end Alembic commands ###
