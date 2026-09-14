from datetime import date

from app.models.audit import AuditLog


def test_dashboard_metrics_after_checkin(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    visitor_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert visitor_response.status_code == 201

    visitor_id = visitor_response.json()["id"]

    checkin_response = client.post(
        "/api/v1/checkin/",
        headers=headers,
        json={
            "visitor_id": visitor_id,
            "purpose": "Project Meeting",
            "host_name": "John Host",
            "host_department": "ICT",
        },
    )

    assert checkin_response.status_code == 201

    response = client.get(
        "/api/v1/dashboard/metrics",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["visitors_today"] == 1
    assert body["currently_checked_in"] == 1
    assert body["visitors_this_week"] == 1


def test_dashboard_recent_visits(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    visitor_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert visitor_response.status_code == 201

    visitor_id = visitor_response.json()["id"]

    checkin_response = client.post(
        "/api/v1/checkin/",
        headers=headers,
        json={
            "visitor_id": visitor_id,
            "purpose": "Security Review",
            "host_name": "Alice Host",
            "host_department": "Cyber Security",
        },
    )

    assert checkin_response.status_code == 201

    response = client.get(
        "/api/v1/dashboard/recent",
        headers=headers,
    )

    assert response.status_code == 200

    visits = response.json()

    assert len(visits) == 1
    assert visits[0]["visitor_id"] == visitor_id
    assert visits[0]["purpose"] == "Security Review"


def test_report_summary_counts_visits(
    client,
    admin_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "admin")

    visitor_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert visitor_response.status_code == 201

    visitor_id = visitor_response.json()["id"]

    checkin_response = client.post(
        "/api/v1/checkin/",
        headers=headers,
        json={
            "visitor_id": visitor_id,
            "purpose": "Project Meeting",
            "host_name": "John Host",
            "host_department": "ICT",
        },
    )

    assert checkin_response.status_code == 201

    today = date.today().isoformat()

    response = client.get(
        "/api/v1/reports/summary",
        headers=headers,
        params={
            "start_date": today,
            "end_date": today,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_visits"] == 1
    assert body["unique_visitors"] == 1
    assert body["purpose_breakdown"]["Project Meeting"] == 1


def test_manager_can_access_report_summary(
    client,
    manager_user,
    auth_header,
):
    headers = auth_header(client, "manager")

    today = date.today().isoformat()

    response = client.get(
        "/api/v1/reports/summary",
        headers=headers,
        params={
            "start_date": today,
            "end_date": today,
        },
    )

    assert response.status_code == 200


def test_guard_cannot_access_report_summary(
    client,
    guard_user,
    auth_header,
):
    headers = auth_header(client, "guard")

    today = date.today().isoformat()

    response = client.get(
        "/api/v1/reports/summary",
        headers=headers,
        params={
            "start_date": today,
            "end_date": today,
        },
    )

    assert response.status_code == 403


def test_admin_can_export_pdf_report(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.get(
        "/api/v1/reports/export/pdf",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_manager_can_export_pdf_report(
    client,
    manager_user,
    auth_header,
):
    headers = auth_header(client, "manager")

    response = client.get(
        "/api/v1/reports/export/pdf",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_guard_cannot_export_pdf_report(
    client,
    guard_user,
    auth_header,
):
    headers = auth_header(client, "guard")

    response = client.get(
        "/api/v1/reports/export/pdf",
        headers=headers,
    )

    assert response.status_code == 403


def test_visitor_history_returns_visit_records(
    client,
    guard_user,
    auth_header,
    visitor_payload,
):
    headers = auth_header(client, "guard")

    visitor_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert visitor_response.status_code == 201

    visitor_id = visitor_response.json()["id"]

    checkin_response = client.post(
        "/api/v1/checkin/",
        headers=headers,
        json={
            "visitor_id": visitor_id,
            "purpose": "Research Meeting",
            "host_name": "Test Host",
            "host_department": "Research",
        },
    )

    assert checkin_response.status_code == 201

    response = client.get(
        f"/api/v1/reports/visitor/{visitor_id}/history",
        headers=headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["visitor_id"] == visitor_id
    assert history[0]["purpose"] == "Research Meeting"


def test_audit_log_contains_expected_fields(
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
    assert audit.id is not None
    assert audit.user_id == guard_user.id
    assert audit.action == "create"
    assert audit.resource_type == "visitor"
    assert audit.resource_id == visitor_id
    assert audit.timestamp is not None


def test_dashboard_requires_authentication(client):
    response = client.get(
        "/api/v1/dashboard/metrics"
    )

    assert response.status_code == 401


def test_pdf_report_requires_authentication(client):
    response = client.get(
        "/api/v1/reports/export/pdf"
    )

    assert response.status_code == 401