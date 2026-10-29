import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.core.database import Base
from app.core.security import get_password_hash, create_access_token
from app.main import app
from app.models import (
    Organization,
    User,
    UserRole,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_org(db):
    org = Organization(name="Test Org")
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture(scope="function")
def test_user(db, test_org):
    user = User(
        org_id=test_org.id,
        email="maya.test@example.com",
        full_name="Maya Resource Manager",
        role=UserRole.RESOURCE_MANAGER,
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def delivery_head_user(db, test_org):
    user = User(
        org_id=test_org.id,
        email="daniel.head@example.com",
        full_name="Daniel Delivery Head",
        role=UserRole.DELIVERY_HEAD,
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    token = create_access_token(
        subject=test_user.id,
        org_id=test_user.org_id,
        role=test_user.role.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def delivery_head_headers(delivery_head_user):
    token = create_access_token(
        subject=delivery_head_user.id,
        org_id=delivery_head_user.org_id,
        role=delivery_head_user.role.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
