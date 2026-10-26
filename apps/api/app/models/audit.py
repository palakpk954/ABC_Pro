from sqlalchemy import JSON, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


class AuditLog(TenantModel):
    __tablename__ = "audit_logs"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(100), nullable=False, index=True)  # create, update, delete, approve_plan, etc.
    entity_type = Column(String(100), nullable=False, index=True)  # employee, project, plan, assignment
    entity_id = Column(String(36), nullable=False, index=True)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User")
