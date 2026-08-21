"""add reviews table for ratings & reviews

Revision ID: c7f2a91d4e63
Revises: 605030253d2c
Create Date: 2026-08-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7f2a91d4e63'
down_revision = '605030253d2c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('place_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['place_id'], ['heritage_places.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('place_id', 'user_id', name='uq_reviews_place_user')
    )
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reviews_place_id'), ['place_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_reviews_user_id'), ['user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reviews_user_id'))
        batch_op.drop_index(batch_op.f('ix_reviews_place_id'))
    op.drop_table('reviews')
