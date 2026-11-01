"""initial create links table

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("clicks", sa.BigInteger(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_links_code"), "links", ["code"], unique=True)
    op.create_index(op.f("ix_links_id"), "links", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_links_id"), table_name="links")
    op.drop_index(op.f("ix_links_code"), table_name="links")
    op.drop_table("links")
