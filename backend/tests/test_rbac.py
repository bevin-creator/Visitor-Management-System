#admin can access report summary test
def test_admin_can_access_report_summary(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.get(
        "/api/v1/reports/summary",
        params={
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
        headers=headers,
    )

    assert response.status_code == 200

#manager can access report summary test
def test_manager_can_access_report_summary(
    client,
    manager_user,
    auth_header,
):
    headers = auth_header(client, "manager")

    response = client.get(
        "/api/v1/reports/summary",
        params={
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
        headers=headers,
    )

    assert response.status_code == 200

#guard cannot access reports test
def test_guard_cannot_access_report_summary(
    client,
    guard_user,
    auth_header,
):
    headers = auth_header(client, "guard")

    response = client.get(
        "/api/v1/reports/summary",
        params={
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
        headers=headers,
    )

    assert response.status_code == 403

#user management rbac checks 
def test_admin_can_access_user_registration(
    client,
    admin_user,
    auth_header,
):
    headers = auth_header(client, "admin")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "rbacguard",
            "email": "rbacguard@example.com",
            "password": "TestPass123!",
            "full_name": "RBAC Guard",
            "role": "guard",
        },
    )

    assert response.status_code == 200

def test_manager_cannot_access_user_registration(
    client,
    manager_user,
    auth_header,
):
    headers = auth_header(client, "manager")

    response = client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "username": "blockedmanager",
            "email": "blockedmanager@example.com",
            "password": "TestPass123!",
            "full_name": "Blocked Manager",
            "role": "guard",
        },
    )

    assert response.status_code == 403