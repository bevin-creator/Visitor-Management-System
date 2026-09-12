from app.models.audit import AuditLog

import pytest

#test visitor life cycle
def test_complete_visitor_checkin_checkout_workflow(
    client,
    guard_user,
    auth_header,
    visitor_payload,
    db_session,
):

    headers = auth_header(client, "guard")

    # Step 1: Register visitor
    visitor_response = client.post(
        "/api/v1/visitors/",
        headers=headers,
        json=visitor_payload,
    )

    assert visitor_response.status_code == 201

    visitor = visitor_response.json()
    visitor_id = visitor["id"]

    #test visitor checkin
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

    checkin = checkin_response.json()

    assert checkin["visitor_id"] == visitor_id
    assert checkin["checkout_time"] is None

    #active visit verification
    active_response = client.get(
        "/api/v1/checkin/active",
        headers=headers,
    )

    assert active_response.status_code == 200

    active_visits = active_response.json()

    assert len(active_visits) == 1

    active_visit = active_visits[0]

    assert active_visit["visitor_id"] == visitor_id

#visitor checkout
    visit_id = checkin["id"]

    checkout_response = client.post(
        f"/api/v1/checkin/{visit_id}/checkout",
        headers=headers,
    )

    assert checkout_response.status_code == 200

    checkout = checkout_response.json()

    assert checkout["id"] == visit_id
    assert checkout["checkout_time"] is not None

#test visitor disappers from active visits
    active_after_checkout = client.get(
        "/api/v1/checkin/active",
        headers=headers,
    )

    assert active_after_checkout.status_code == 200
    assert active_after_checkout.json() == []

#audit verification 
    audit_actions = [
        row.action
        for row in db_session.query(AuditLog).all()
    ]

    assert "create" in audit_actions
    assert "checkin" in audit_actions
    assert "checkout" in audit_actions

#checkout twice should fail
def test_second_checkout_is_rejected(
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
            "purpose": "Meeting",
            "host_name": "John Host",
            "host_department": "ICT",
        },
    )

    assert checkin_response.status_code == 201

    visit_id = checkin_response.json()["id"]

    first_checkout = client.post(
        f"/api/v1/checkin/{visit_id}/checkout",
        headers=headers,
    )

    assert first_checkout.status_code == 200

    second_checkout = client.post(
        f"/api/v1/checkin/{visit_id}/checkout",
        headers=headers,
    )

    assert second_checkout.status_code == 400

#checkout non existent visit
def test_checkout_unknown_visit_returns_404(
    client,
    guard_user,
    auth_header,
):
    headers = auth_header(client, "guard")

    response = client.post(
        "/api/v1/checkin/999999/checkout",
        headers=headers,
    )

    assert response.status_code == 404

#reject unauthenticated check-in
def test_checkin_requires_authentication(
    client,
):
    response = client.post(
        "/api/v1/checkin/",
        json={
            "visitor_id": 1,
            "purpose": "Meeting",
            "host_name": "John Host",
            "host_department": "ICT",
        },
    )

    assert response.status_code == 401

#reject unauthenticated list access
def test_active_visits_require_authentication(client):
    response = client.get(
        "/api/v1/checkin/active"
    )

    assert response.status_code == 401

#security regression test
@pytest.mark.xfail(
    reason="Current implementation allows duplicate active check-ins"
)
def test_duplicate_active_checkin_is_rejected(
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

    payload = {
        "visitor_id": visitor_id,
        "purpose": "Meeting",
        "host_name": "John Host",
        "host_department": "ICT",
    }

    first_checkin = client.post(
        "/api/v1/checkin/",
        headers=headers,
        json=payload,
    )

    assert first_checkin.status_code == 201

    second_checkin = client.post(
        "/api/v1/checkin/",
        headers=headers,
        json=payload,
    )

    assert second_checkin.status_code in (400, 409)