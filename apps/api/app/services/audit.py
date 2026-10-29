from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import AuditLog


def log_audit_event(
    db: Session,
    org_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    user_id: Optional[str] = None,
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Creates an immutable audit log record for a state change."""
    log_entry = AuditLog(
        org_id=org_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        before_state=before_state,
        after_state=after_state,
        ip_address=ip_address,
    )
    db.add(log_entry)
    db.flush()
    return log_entry
