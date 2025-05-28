"""Add client_id to message_batches

Revision ID: e9702592451c
Revises: 37bae2d2c9ec
Create Date: 2025-05-28 12:02:06.784245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9702592451c'
down_revision: Union[str, None] = '37bae2d2c9ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('message_batches',
                sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_message_batches_client_id',
        'message_batches',
        'clients',
        ['client_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_column('message_batches', 'client_id')
