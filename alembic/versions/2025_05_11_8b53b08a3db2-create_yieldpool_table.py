"""Create YieldPool Table

Revision ID: 8b53b08a3db2
Revises: 
Create Date: 2025-05-11 18:39:40.133789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b53b08a3db2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'yield_pools',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chain', sa.String(), nullable=False),
        sa.Column('project', sa.String(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('tvlUsd', sa.Float(), nullable=False),
        sa.Column('apyBase', sa.Float(), nullable=True),
        sa.Column('apyReward', sa.Float(), nullable=True),
        sa.Column('apy', sa.Float(), nullable=False),
        sa.Column('apyPct1D', sa.Float(), nullable=True),
        sa.Column('apyPct7D', sa.Float(), nullable=True),
        sa.Column('apyPct30D', sa.Float(), nullable=True),
        sa.Column('stablecoin', sa.Boolean(), nullable=True),
        sa.Column('rewardTokens', sa.JSON(), nullable=True),
        sa.Column('pool', sa.String(), nullable=False),
        sa.Column('underlyingTokens', sa.JSON(), nullable=True),
        sa.Column('ilRisk', sa.String(), nullable=True),
        sa.Column('exposure', sa.String(), nullable=True),
        sa.Column('predictedClass', sa.String(), nullable=True),
        sa.Column('predictedProb', sa.Float(), nullable=True),
        sa.Column('binnedConfidence', sa.Float(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('volumeUsd1d', sa.Float(), nullable=True),
        sa.Column('volumeUsd7d', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for frequently queried fields
    op.create_index(op.f('ix_yield_pools_chain'), 'yield_pools', ['chain'], unique=False)
    op.create_index(op.f('ix_yield_pools_project'), 'yield_pools', ['project'], unique=False)
    op.create_index(op.f('ix_yield_pools_symbol'), 'yield_pools', ['symbol'], unique=False)
    op.create_index(op.f('ix_yield_pools_pool'), 'yield_pools', ['pool'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_yield_pools_pool'), table_name='yield_pools')
    op.drop_index(op.f('ix_yield_pools_symbol'), table_name='yield_pools')
    op.drop_index(op.f('ix_yield_pools_project'), table_name='yield_pools')
    op.drop_index(op.f('ix_yield_pools_chain'), table_name='yield_pools')
    # Then drop the table
    op.drop_table('yield_pools')
