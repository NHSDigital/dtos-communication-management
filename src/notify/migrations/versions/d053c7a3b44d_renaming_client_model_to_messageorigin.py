"""Renaming Client model to MessageOrigin

Revision ID: d053c7a3b44d
Revises: e9702592451c
Create Date: 2025-07-11 15:20:24.337586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd053c7a3b44d'
down_revision: Union[str, None] = 'e9702592451c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### create message_origins table ###
    op.create_table('message_origins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    # ### add foreign key to message_batches ###
    op.add_column('message_batches',
                sa.Column('message_origin_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_message_batches_message_origin_id',
        'message_batches',
        'message_origins',
        ['message_origin_id'],
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
    # ### Drop message_origins ###
    op.drop_constraint(op.f('fk_message_batches_message_origin_id'), 'message_batches', type_='foreignkey')
    op.drop_column('message_batches', 'message_origin_id')
    op.drop_table('message_origins')
    # ### end Alembic commands ###
