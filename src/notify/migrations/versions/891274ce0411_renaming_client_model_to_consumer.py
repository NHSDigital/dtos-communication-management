"""Renaming Client model to Consumer

Revision ID: 891274ce0411
Revises: e9702592451c
Create Date: 2025-07-15 11:33:33.061927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '891274ce0411'
down_revision: Union[str, None] = 'e9702592451c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### create consumers table ###
    op.create_table('consumers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    # ### add foreign key to message_batches ###
    op.add_column('message_batches',
                sa.Column('consumer_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_message_batches_consumer_id',
        'message_batches',
        'consumers',
        ['consumer_id'],
        ['id'],
        ondelete='CASCADE'
    )
    # ### drop clients ###
    op.drop_constraint(op.f('fk_message_batches_client_id'), 'message_batches', type_='foreignkey')
    op.drop_column('message_batches', 'client_id')
    op.drop_table('clients')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Add client back ###
    op.create_table('clients',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), autoincrement=False, nullable=True),
    sa.Column('description', sa.String(), autoincrement=False, nullable=True),
    sa.Column('key', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('message_batches', sa.Column('client_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('fk_message_batches_client_id'), 'message_batches', 'clients', ['client_id'], ['id'], ondelete='CASCADE')
    # ### Drop consumers ###
    op.drop_constraint(op.f('fk_message_batches_consumer_id'), 'message_batches', type_='foreignkey')
    op.drop_column('message_batches', 'consumer_id')
    op.drop_table('consumers')
    # ### end Alembic commands ###
