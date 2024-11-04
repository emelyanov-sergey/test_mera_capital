"""Initial commit + Add DeribitIndex model

Revision ID: d1a0fe64e6a6
Revises: 
Create Date: 2024-11-04 00:37:28.006759

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d1a0fe64e6a6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "deribit_index",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("price", sa.Numeric(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_deribit_index_id"), "deribit_index", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_deribit_index_id"), table_name="deribit_index")
    op.drop_table("deribit_index")
