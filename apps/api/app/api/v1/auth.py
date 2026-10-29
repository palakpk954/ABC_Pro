from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.models import User
from app.schemas.auth import Token, UserResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    access_token = create_access_token(
        subject=user.id,
        org_id=user.org_id,
        role=user.role.value,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        org_id=user.org_id,
        role=user.role.value,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.post("/token", response_model=Token, include_in_schema=False)
def login_form_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 compatible form endpoint for Swagger UI authorization."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        org_id=user.org_id,
        role=user.role.value,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        org_id=user.org_id,
        role=user.role.value,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
