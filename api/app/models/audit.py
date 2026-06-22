"""GDPR audit log (US11b).

Records data-subject actions (export, delete). user_id is stored as a plain
string — NOT a foreign key — so the record survives account deletion.
"""
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import GUID, Base, TimestampMixin

GDPR_EXPORT = "export"
GDPR_DELETE = "delete"


class GdprAuditLog(Base, TimestampMixin):
    __tablename__ = "gdpr_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Deliberately not a FK: must outlive the deleted user.
    user_id: Mapped[str] = mapped_column(GUID(), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
