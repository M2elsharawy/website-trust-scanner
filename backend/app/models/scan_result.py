import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScanResult(Base):
    """Persisted scan result — linked to a Site for verified owners."""

    __tablename__ = "scan_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Snapshot of domain at scan time (site domain can change)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    trust_score: Mapped[int] = mapped_column(Integer, nullable=False)
    # Full result dict — safe, sanitised by compute_trust_report()
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ScanResult site_id={self.site_id!r} score={self.trust_score!r}>"
