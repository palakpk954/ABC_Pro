from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
