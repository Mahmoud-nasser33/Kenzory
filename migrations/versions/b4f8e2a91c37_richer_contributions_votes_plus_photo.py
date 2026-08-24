"""richer contributions: votes + photo captions

Revision ID: b4f8e2a91c37
Revises: c7f2a91d4e63
Create Date: 2026-08-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4f8e2a91c37'
down_revision = 'c7f2a91d4e63'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('submission_votes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('submission_id', 'user_id', name='uq_votes_submission_user')
    )
    with op.batch_alter_table('submission_votes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_submission_votes_submission_id'), ['submission_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_submission_votes_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('submissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_captions', sa.JSON(), nullable=True))

    with op.batch_alter_table('heritage_places', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo_captions', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('heritage_places', schema=None) as batch_op:
        batch_op.drop_column('photo_captions')
    with op.batch_alter_table('submissions', schema=None) as batch_op:
        batch_op.drop_column('image_captions')
    with op.batch_alter_table('submission_votes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_submission_votes_user_id'))
        batch_op.drop_index(batch_op.f('ix_submission_votes_submission_id'))
    op.drop_table('submission_votes')
