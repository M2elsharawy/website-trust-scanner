"""admin_leads: leads table

Revision ID: 002
Revises: 001
Create Date: 2026-06-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

_LEAD_STATUSES = (
    "new",
    "contacted",
    "interested",
    "permission_requested",
    "verified",
    "active_client",
    "rejected",
    "do_not_contact",
)


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("domain", sa.String(253), nullable=False, unique=True),
        sa.Column(
            "status",
            sa.Enum(*_LEAD_STATUSES, name="lead_status"),
            nullable=False,
            server_default="new",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("added_by", sa.String(255), nullable=True),
        sa.Column("last_audit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_lead_score", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_leads_domain", "leads", ["domain"], unique=True)
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_created_at", "leads", ["created_at"])


def downgrade() -> None:
    op.drop_table("leads")
    op.execute("DROP TYPE IF EXISTS lead_status")
