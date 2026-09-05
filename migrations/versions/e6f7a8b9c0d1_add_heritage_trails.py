"""add heritage trails tables

Revision ID: e6f7a8b9c0d1
Revises: d4e5f6a7b8c9
Create Date: 2026-09-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6f7a8b9c0d1'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'trails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=160), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image', sa.String(length=255), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('trails', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_trails_slug'), ['slug'], unique=True)
        batch_op.create_index(batch_op.f('ix_trails_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_trails_created_by'), ['created_by'], unique=False)

    op.create_table(
        'trail_stops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trail_id', sa.Integer(), nullable=False),
        sa.Column('place_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['place_id'], ['heritage_places.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trail_id'], ['trails.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trail_id', 'place_id', name='uq_trail_stop'),
    )
    with op.batch_alter_table('trail_stops', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_trail_stops_trail_id'), ['trail_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_trail_stops_place_id'), ['place_id'], unique=False)


def downgrade():
    with op.batch_alter_table('trail_stops', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_trail_stops_place_id'))
        batch_op.drop_index(batch_op.f('ix_trail_stops_trail_id'))

    op.drop_table('trail_stops')
    with op.batch_alter_table('trails', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_trails_created_by'))
        batch_op.drop_index(batch_op.f('ix_trails_created_at'))
        batch_op.drop_index(batch_op.f('ix_trails_slug'))

    op.drop_table('trails')