import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    interested = "interested"
    permission_requested = "permission_requested"
    verified = "verified"
    active_client = "active_client"
    rejected = "rejected"
    do_not_contact = "do_not_contact"


# Allowed next-state transitions. Terminal states have empty sets.
LEAD_STATUS_TRANSITIONS: dict[LeadStatus, set[LeadStatus]] = {
    LeadStatus.new: {
        LeadStatus.contacted,
        LeadStatus.rejected,
        LeadStatus.do_not_contact,
    },
    LeadStatus.contacted: {
        LeadStatus.interested,
        LeadStatus.rejected,
        LeadStatus.do_not_contact,
    },
    LeadStatus.interested: {
        LeadStatus.permission_requested,
        LeadStatus.rejected,
        LeadStatus.do_not_contact,
    },
    LeadStatus.permission_requested: {
        LeadStatus.verified,
        LeadStatus.rejected,
        LeadStatus.do_not_contact,
    },
    LeadStatus.verified: {
        LeadStatus.active_client,
        LeadStatus.rejected,
    },
    LeadStatus.active_client: {
        LeadStatus.rejected,
    },
    LeadStatus.rejected: {
        LeadStatus.do_not_contact,
    },
    LeadStatus.do_not_contact: set(),  # terminal
}

# Statuses where running an audit is forbidden
LEAD_AUDIT_BLOCKED_STATUSES: frozenset[LeadStatus] = frozenset(
    {LeadStatus.rejected, LeadStatus.do_not_contact}
)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    domain: Mapped[str] = mapped_column(String(253), nullable=False, unique=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status"), nullable=False, default=LeadStatus.new
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Last audit snapshot (avoids separate join for list view)
    last_audit_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Lead domain={self.domain!r} status={self.status.value!r}>"
