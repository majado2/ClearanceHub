from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    performed_by_email: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> AuditLog:
    audit = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by_email=performed_by_email,
        metadata_json=metadata,
    )
    db.add(audit)
    db.flush()
    return audit
