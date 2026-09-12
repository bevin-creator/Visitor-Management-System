import pytest

from app.models.audit import AuditLog
from app.models.user import User
from app.routers.auth import get_password_hash


@pytest.mark.xfail(
    reason="Current authentication does not enforce User.is_active"
)
def test_inactive_user_cannot_login(
    client,
    db_session,
):
    user = User(
        username="inactiveuser",
        email="inactive@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Inactive User",
        role="guard",
        is_active=False,
    )

    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "inactiveuser",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 401


@pytest.mark.xfail(
    reason="Current user schema does not restrict role to approved values"
)
def test_unknown_role_is_rejected(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "superuser1",
            "email": "superuser1@example.com",
            "password": "TestPass123!",
            "full_name": "Unexpected Role User",
            "role": "superuser",
        },
    )

    assert response.status_code in (400, 422)


@pytest.mark.xfail(
    reason="Current visitor retrieval exposes decrypted phone and ID to Guard role"
)
def test_guard_cannot_retrieve_full_sensitive_visitor_record(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    create_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert create_response.status_code == 201

    visitor_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/visitors/{visitor_id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["phone"] != visitor_payload["phone"]
    assert body["id_number"] != visitor_payload["id_number"]


@pytest.mark.xfail(
    reason="Current backend allows authenticated Guard users to update visitor records"
)
def test_guard_cannot_update_visitor(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    create_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert create_response.status_code == 201

    visitor_id = create_response.json()["id"]

    updated_payload = {
        **visitor_payload,
        "full_name": "Modified Visitor",
    }

    response = client.put(
        f"/api/v1/visitors/{visitor_id}",
        headers=headers,
        json=updated_payload,
    )

    assert response.status_code == 403


@pytest.mark.xfail(
    reason="Current implementation does not audit sensitive visitor read access"
)
def test_sensitive_visitor_read_is_audited(
    client,
    guard_user,
    auth_header,
    visitor_payload,
    db_session,
):
    headers = auth_header(client, "guard")

    create_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert create_response.status_code == 201

    visitor_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/visitors/{visitor_id}",
        headers=headers,
    )

    assert response.status_code == 200

    read_audit = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.user_id == guard_user.id,
            AuditLog.resource_type == "visitor",
            AuditLog.resource_id == visitor_id,
            AuditLog.action.in_(
                ["read", "view", "access"]
            ),
        )
        .first()
    )

    assert read_audit is not None


@pytest.mark.xfail(
    reason="Current general visitor endpoint returns full decrypted ID to Manager"
)
def test_manager_does_not_receive_full_id_number(
    client,
    manager_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "manager")

    create_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert create_response.status_code == 201

    visitor_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/visitors/{visitor_id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id_number"] != visitor_payload["id_number"]


@pytest.mark.xfail(
    reason="Current PDF report export is not recorded in the audit log"
)
def test_pdf_export_is_audited(
    client,
    admin_user,
    auth_header,
    db_session,
):
    headers = auth_header(client, "admin")

    response = client.get(
        "/api/v1/reports/export/pdf",
        headers=headers,
    )

    assert response.status_code == 200

    audit = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.user_id == admin_user.id,
            AuditLog.action.in_(
                ["export", "report_export", "pdf_export"]
            ),
        )
        .first()
    )

    assert audit is not None