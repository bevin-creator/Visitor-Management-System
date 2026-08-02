#Audit logging service
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_action(
    db: Session,
    action: str,
    resource_type: str,
    user_id: int = None,
    resource_id: int = None,
    details: str = None,
    ip_address: str = None
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()