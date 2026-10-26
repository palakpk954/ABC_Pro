import enum
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.models.base import TenantModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RESOURCE_MANAGER = "resource_manager"
    DELIVERY_HEAD = "delivery_head"
    TEAM_LEAD = "team_lead"


class User(TenantModel):
    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.RESOURCE_MANAGER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
