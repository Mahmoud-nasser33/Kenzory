"""add user bio and level for community profiles

Revision ID: a1b2c3d4e5f6
Revises: b4f8e2a91c37
Create Date: 2026-08-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'b4f8e2a91c37'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('level', sa.String(length=40), nullable=False, server_default='Contributor'))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('level')
        batch_op.drop_column('bio')
