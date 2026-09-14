from app.routers.auth import get_password_hash, verify_password

from app.models.audit import AuditLog

#test password hashing
def test_password_hash_and_verify():
    password = "StrongPass123!"

    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


#wrong password test
def test_wrong_password_fails():
    password = "StrongPass123!"

    hashed = get_password_hash(password)

    assert verify_password("WrongPassword", hashed) is False

#successful login test

def test_login_success(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["role"] == "admin"
    assert body["username"] == "admin"

#incorrect login test
def test_login_wrong_password(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == 401

#test nonexistent user
def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "doesnotexist",
            "password": "Anything123!",
        },
    )

    assert response.status_code == 401

#test protected endpoint
def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401

#authenticated /me test
def test_me_returns_current_user(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "admin"
    assert body["role"] == "admin"

#add audit-login test 
def test_successful_login_creates_audit_log(
    client,
    admin_user,
    db_session,
):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 200

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "login")
        .first()
    )

    assert audit is not None
    assert audit.user_id == admin_user.id