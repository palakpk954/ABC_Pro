from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """Extract and validate JWT token, returning the authenticated user.
    Falls back to first active user if in development and no token is passed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        # Development fallback: if dev mode, allow using default admin/user for seamless testing
        if settings.ENVIRONMENT == "development":
            dev_user = db.query(User).filter(User.is_active.is_(True)).first()
            if dev_user:
                return dev_user
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        org_id: str = payload.get("org_id")
        if user_id is None or org_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    user = db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def get_current_tenant_id(
    current_user: User = Depends(get_current_user),
) -> str:
    """Returns the tenant organization ID of current user."""
    return current_user.org_id


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensures current user has admin privileges."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have administrative privileges",
        )
    return current_user
