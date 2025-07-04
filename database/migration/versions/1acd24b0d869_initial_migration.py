"""Initial migration

Revision ID: 1acd24b0d869
Revises:
Create Date: 2025-06-15 14:37:08.210755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1acd24b0d869'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('lang', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
