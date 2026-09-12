from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.models.user import User
from app.models.visitor import Visitor, VisitRecord
from app.models.audit import AuditLog

import pytest

from app.main import app
from app.database import Base, get_db

from app.routers.auth import get_password_hash


TEST_DATABASE_URL = "sqlite://"


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()

        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

'''
#admin creation helper
@pytest.fixture
def admin_user(db_session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Test Administrator",
        role="admin",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user
'''
#reusable login helper
@pytest.fixture
def auth_header():

    def make_header(client, username, password="TestPass123!"):
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": username,
                "password": password,
            },
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        return {
            "Authorization": f"Bearer {token}"
        }

    return make_header

#user creation helper 
def create_test_user(
    db_session,
    username,
    role,
    password="TestPass123!",
    email=None,
    is_active=True,
):
    user = User(
        username=username,
        email=email or f"{username}@example.com",
        hashed_password=get_password_hash(password),
        full_name=f"{role.title()} Test User",
        role=role,
        is_active=is_active,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user

@pytest.fixture
def admin_user(db_session):
    return create_test_user(
        db_session,
        username="admin",
        role="admin",
    )


@pytest.fixture
def manager_user(db_session):
    return create_test_user(
        db_session,
        username="manager",
        role="manager",
    )


@pytest.fixture
def guard_user(db_session):
    return create_test_user(
        db_session,
        username="guard",
        role="guard",
    )

#visitor fixture 
@pytest.fixture
def visitor_payload():
    return {
        "full_name": "Visitor One",
        "email": "visitor1@example.com",
        "phone": "+254700123456",
        "company": "Example Ltd",
        "id_type": "National ID",
        "id_number": "12345678",
    }