from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Dialect, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from app.db.base import Base


class _InetOrText(TypeDecorator):
    """
    Stores INET on PostgreSQL; falls back to VARCHAR(45) on SQLite (tests).
    Prevents test failures when pytest uses SQLite instead of PostgreSQL.
    """

    impl = String(45)
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(INET())
        return dialect.type_descriptor(String(45))


class AuditLog(Base):
    """
    Append-only audit trail.  No UPDATE or DELETE should ever be issued
    against this table.  actor_ip is stored but NEVER returned via the API.
    """

    __tablename__ = "audit_logs"

    # BigSerial gives ordered, sequential IDs for easy pagination without gaps
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Who performed the action
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # UUID str
    actor_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    actor_ip: Mapped[str | None] = mapped_column(_InetOrText(), nullable=True)

    # What happened
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Sanitised details (no secrets, no raw HTML, no file contents)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    outcome: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r} outcome={self.outcome!r}>"
