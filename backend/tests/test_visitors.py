from sqlalchemy import text

from app.models.visitor import Visitor
from app.models.audit import AuditLog
from app.services.encryption import blind_index

#test authenticated guard can register visitor
def test_guard_can_register_visitor(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["full_name"] == "Visitor One"
    assert body["email"] == "visitor1@example.com"
    assert body["phone"] == "+254700123456"
    assert body["id_type"] == "National ID"
    assert body["id_number"] == "12345678"

#test visitor persistence
def test_registered_visitor_is_saved_to_database(
    client,
    guard_user,
    auth_header,
    visitor_payload,
    db_session,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    visitor_id = response.json()["id"]

    saved_visitor = (
        db_session.query(Visitor)
        .filter(Visitor.id == visitor_id)
        .first()
    )

    assert saved_visitor is not None
    assert saved_visitor.full_name == "Visitor One"
    assert saved_visitor.email == "visitor1@example.com"

#verify blind indexes
def test_visitor_blind_indexes_are_generated(
    client,
    guard_user,
    auth_header,
    visitor_payload,
    db_session,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    visitor_id = response.json()["id"]

    saved_visitor = (
        db_session.query(Visitor)
        .filter(Visitor.id == visitor_id)
        .first()
    )

    assert saved_visitor.phone_bidx == blind_index(
        visitor_payload["phone"]
    )

    assert saved_visitor.id_number_bidx == blind_index(
        visitor_payload["id_number"]
    )

#encrypted at rest test
def test_sensitive_visitor_data_is_encrypted_at_rest(
    client,
    guard_user,
    auth_header,
    visitor_payload,
    db_session,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    visitor_id = response.json()["id"]

    row = db_session.execute(
        text(
            """
            SELECT phone, id_number, phone_bidx, id_number_bidx
            FROM visitors
            WHERE id = :visitor_id
            """
        ),
        {
            "visitor_id": visitor_id
        },
    ).mappings().one()

    assert row["phone"] != visitor_payload["phone"]
    assert row["id_number"] != visitor_payload["id_number"]

    assert row["phone_bidx"] == blind_index(
        visitor_payload["phone"]
    )

    assert row["id_number_bidx"] == blind_index(
        visitor_payload["id_number"]
    )

#visitor creation creates an audit log
def test_visitor_registration_creates_audit_log(
    client,
    guard_user,
    auth_header,
    visitor_payload,
    db_session,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    visitor_id = response.json()["id"]

    audit = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.action == "create",
            AuditLog.resource_type == "visitor",
            AuditLog.resource_id == visitor_id,
        )
        .first()
    )

    assert audit is not None
    assert audit.user_id == guard_user.id

#test exact phone search 
def test_search_visitor_by_exact_phone(
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

    search_response = client.get(
        "/api/v1/visitors/",
        headers=headers,
        params={
            "search": "+254700123456"
        },
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["full_name"] == "Visitor One"

#test phone formatting normalization
def test_search_phone_ignores_formatting(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    search_response = client.get(
        "/api/v1/visitors/",
        headers=headers,
        params={
            "search": "+254 700-123-456"
        },
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["phone"] == "+254700123456"

#test exact id-number search
def test_search_visitor_by_exact_id_number(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    search_response = client.get(
        "/api/v1/visitors/",
        headers=headers,
        params={
            "search": "12345678"
        },
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["full_name"] == "Visitor One"

#test partial name search
def test_search_visitor_by_partial_name(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    search_response = client.get(
        "/api/v1/visitors/",
        headers=headers,
        params={
            "search": "Visitor"
        },
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["full_name"] == "Visitor One"

#test partial email search 
def test_search_visitor_by_partial_email(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    search_response = client.get(
        "/api/v1/visitors/",
        headers=headers,
        params={
            "search": "visitor1"
        },
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1

#test partial phone search (should not match because this is a blind-index search)
def test_partial_phone_search_does_not_match(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert response.status_code == 201

    search_response = client.get(
        "/api/v1/visitors/",
        headers=headers,
        params={
            "search": "0700"
        },
    )

    assert search_response.status_code == 200
    assert search_response.json() == []

#test retrieving visitor by id
def test_get_visitor_by_id(
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

    assert body["id"] == visitor_id
    assert body["full_name"] == "Visitor One"

#test non existent visitor
def test_get_unknown_visitor_returns_404(
    client,
    guard_user,
    auth_header,
):
    headers = auth_header(client, "guard")

    response = client.get(
        "/api/v1/visitors/999999",
        headers=headers,
    )

    assert response.status_code == 404

#test unauthenticated access
def test_visitor_list_requires_authentication(client):
    response = client.get(
        "/api/v1/visitors/"
    )

    assert response.status_code == 401

def test_visitor_registration_requires_authentication(
    client,
    visitor_payload,
):
    response = client.post(
        "/api/v1/visitors/",
        json=visitor_payload,
    )

    assert response.status_code == 401