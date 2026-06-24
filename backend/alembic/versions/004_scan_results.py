"""scan_results: persisted scan history for verified sites

Revision ID: 004
Revises: 003
Create Date: 2026-06-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "site_id",
            UUID(as_uuid=True),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("trust_score", sa.Integer(), nullable=False),
        sa.Column("result_json", JSONB(), nullable=False),
        sa.Column(
            "scanned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_scan_results_site_id", "scan_results", ["site_id"])
    op.create_index("ix_scan_results_scanned_at", "scan_results", ["scanned_at"])


def downgrade() -> None:
    op.drop_table("scan_results")
