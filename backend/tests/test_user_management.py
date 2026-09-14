from app.models.user import User
from app.models.audit import AuditLog

#admin can create guard test
def test_admin_can_create_guard(
    client,
    admin_user,
    auth_header,
    db_session,
):
    headers = auth_header(client, "admin")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "guard2",
            "email": "guard2@example.com",
            "password": "GuardPass123!",
            "full_name": "Guard Two",
            "role": "guard",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "guard2"
    assert body["email"] == "guard2@example.com"
    assert body["role"] == "guard"

    #verify user was saved in db
    saved_user = (
        db_session.query(User)
        .filter(User.username == "guard2")
        .first()
    )

    assert saved_user is not None
    assert saved_user.role == "guard"

    #verify password is hashed
    assert saved_user.hashed_password != "GuardPass123!"

#test admin can create manager
def test_admin_can_create_manager(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "manager2",
            "email": "manager2@example.com",
            "password": "ManagerPass123!",
            "full_name": "Manager Two",
            "role": "manager",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "manager"

#test guard cannot create user
def test_guard_cannot_create_user(
    client,
    guard_user,
    auth_header,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "illegaluser",
            "email": "illegaluser@example.com",
            "password": "TestPass123!",
            "full_name": "Illegal User",
            "role": "guard",
        },
    )

    assert response.status_code == 403

#test manager cannot create user 
def test_manager_cannot_create_user(
    client,
    manager_user,
    auth_header,
):
    headers = auth_header(client, "manager")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "anotheruser",
            "email": "anotheruser@example.com",
            "password": "TestPass123!",
            "full_name": "Another User",
            "role": "guard",
        },
    )

    assert response.status_code == 403

#test guest user cannot create account
def test_unauthenticated_user_cannot_create_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "anonymouscreate",
            "email": "anonymous@example.com",
            "password": "TestPass123!",
            "full_name": "Anonymous Attempt",
            "role": "guard",
        },
    )

    assert response.status_code == 401

#test duplicate username failure - username must be unique
def test_duplicate_username_is_rejected(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    first_response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "duplicate",
            "email": "first@example.com",
            "password": "TestPass123!",
            "full_name": "First User",
            "role": "guard",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "duplicate",
            "email": "second@example.com",
            "password": "TestPass123!",
            "full_name": "Second User",
            "role": "guard",
        },
    )

    assert second_response.status_code == 400

#test duplicate email failure - email must be unique
def test_duplicate_email_is_rejected(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    first_response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "userone",
            "email": "same@example.com",
            "password": "TestPass123!",
            "full_name": "User One",
            "role": "guard",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "usertwo",
            "email": "same@example.com",
            "password": "TestPass123!",
            "full_name": "User Two",
            "role": "guard",
        },
    )

    assert second_response.status_code == 400

#test user-creation audit
def test_user_creation_creates_audit_log(
    client,
    admin_user,
    auth_header,
    db_session,
):
    headers = auth_header(client, "admin")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "auditguard",
            "email": "auditguard@example.com",
            "password": "TestPass123!",
            "full_name": "Audit Guard",
            "role": "guard",
        },
    )

    assert response.status_code == 200

    audit = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.action == "create",
            AuditLog.resource_type == "user",
        )
        .first()
    )

    assert audit is not None
    assert audit.user_id == admin_user.id

#negative test - arbitrary roles
def test_unknown_role_behavior(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "badrole",
            "email": "badrole@example.com",
            "password": "TestPass123!",
            "full_name": "Bad Role",
            "role": "superuser",
        },
    )

    assert response.status_code in (400, 422)