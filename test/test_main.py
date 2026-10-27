



def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Job Application Tracker"
    }




def test_register_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "sara.test@example.com",
            "password": "1234"
        }
    )

    assert response.status_code == 422




def test_login_rejects_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "missing.user.test@example.com",
            "password": "WrongPass123"
        }
    )

    assert response.status_code == 401






def test_me_rejects_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid.token.value"
        }
    )

    assert response.status_code == 401




def test_me_requires_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401



def test_job_applications_requires_token(client):
    response = client.get("/job-applications/")

    assert response.status_code == 401




def test_create_job_application(client):
    client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "sara.test@example.com",
            "password": "TestPass123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "sara.test@example.com",
            "password": "TestPass123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/job-applications/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company": "Google",
            "job_title": "Data Analyst Intern",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website"
        }
    )

    assert response.status_code == 201
    assert response.json()["company"] == "Google"
    assert response.json()["job_title"] == "Data Analyst Intern"






def test_get_job_applications(client):
    client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "sara.list.test@example.com",
            "password": "TestPass123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "sara.list.test@example.com",
            "password": "TestPass123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/job-applications/",
        headers=headers,
        json={
            "company": "Google",
            "job_title": "Data Analyst",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website"
        }
    )

    response = client.get(
        "/job-applications/",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["company"] == "Google"


def test_update_job_application(client):
    client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "sara.update.test@example.com",
            "password": "TestPass123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "sara.update.test@example.com",
            "password": "TestPass123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/job-applications/",
        headers=headers,
        json={
            "company": "Google",
            "job_title": "Data Analyst",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website"
        }
    )

    application_id = create_response.json()["id"]

    response = client.patch(
        f"/job-applications/{application_id}",
        headers=headers,
        json={"status": "interview"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interview"
    assert response.json()["company"] == "Google"



def test_delete_job_application(client):
    client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "sara.delete.test@example.com",
            "password": "TestPass123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "sara.delete.test@example.com",
            "password": "TestPass123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/job-applications/",
        headers=headers,
        json={
            "company": "Google",
            "job_title": "Data Analyst",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website"
        }
    )

    application_id = create_response.json()["id"]

    response = client.delete(
        f"/job-applications/{application_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Deleted successfully"

    list_response = client.get(
        "/job-applications/",
        headers=headers
    )

    assert list_response.status_code == 200
    assert list_response.json() == []



# Helper functions for tests

def _register_and_login(
    client,
    email="sara@example.com",
    password="TestPass123",
    name="Sara"
):
    register_response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def _create_application(client, headers, company="Google"):
    response = client.post(
        "/job-applications/",
        headers=headers,
        json={
            "company": company,
            "job_title": "Data Analyst Intern",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website"
        }
    )

    assert response.status_code == 201

    return response.json()


#Successful registration
def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "newuser@example.com",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Sara"
    assert "hashed_password" not in response.json()


#Reject duplicate email
def test_register_rejects_duplicate_email(client):
    data = {
        "name": "Sara",
        "email": "duplicate@example.com",
        "password": "TestPass123"
    }

    first = client.post("/auth/register", json=data)
    second = client.post("/auth/register", json=data)

    assert first.status_code == 201
    assert second.status_code == 409


# Reject wrong password
def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Sara",
            "email": "wrongpass@example.com",
            "password": "TestPass123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPass123"
        }
    )

    assert response.status_code == 401


# Return current user
def test_me_returns_current_user(client):
    headers = _register_and_login(client)

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Sara"
    assert response.json()["email"] == "sara@example.com"


# Reject creating an application without a token
def test_create_application_requires_token(client):
    response = client.post(
        "/job-applications/",
        json={
            "company": "Google",
            "job_title": "Data Analyst",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website"
        }
    )

    assert response.status_code == 401


# Retrieve one application
def test_get_single_application(client):
    headers = _register_and_login(client)
    application = _create_application(client, headers)

    response = client.get(
        f"/job-applications/{application['id']}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["company"] == "Google"


# Users see only their own applications
def test_user_sees_only_own_applications(client):
    first_headers = _register_and_login(
        client,
        email="first@example.com"
    )
    _create_application(client, first_headers)

    second_headers = _register_and_login(
        client,
        email="second@example.com"
    )

    response = client.get(
        "/job-applications/",
        headers=second_headers
    )

    assert response.status_code == 200
    assert response.json() == []


# Reject an invalid status
def test_update_rejects_invalid_status(client):
    headers = _register_and_login(client)
    application = _create_application(client, headers)

    response = client.patch(
        f"/job-applications/{application['id']}",
        headers=headers,
        json={"status": "invalid_status"}
    )

    assert response.status_code == 422


# Prevent updating another user's application
def test_user_cannot_update_another_users_application(client):
    owner_headers = _register_and_login(
        client,
        email="owner@example.com"
    )
    application = _create_application(client, owner_headers)

    other_headers = _register_and_login(
        client,
        email="other@example.com"
    )

    response = client.patch(
        f"/job-applications/{application['id']}",
        headers=other_headers,
        json={"status": "interview"}
    )

    assert response.status_code == 404


# Prevent deleting another user's application
def test_user_cannot_delete_another_users_application(client):
    owner_headers = _register_and_login(
        client,
        email="delete-owner@example.com"
    )
    application = _create_application(client, owner_headers)

    other_headers = _register_and_login(
        client,
        email="delete-other@example.com"
    )

    response = client.delete(
        f"/job-applications/{application['id']}",
        headers=other_headers
    )

    assert response.status_code == 404

    owner_response = client.get(
        f"/job-applications/{application['id']}",
        headers=owner_headers
    )

    assert owner_response.status_code == 200


# Change password successfully
def test_change_password_success(client):
    headers = _register_and_login(client)

    change_response = client.patch(
        "/auth/password",
        headers=headers,
        json={
            "current_password": "TestPass123",
            "new_password": "NewPass456"
        }
    )

    assert change_response.status_code == 200

    new_login = client.post(
        "/auth/login",
        json={
            "email": "sara@example.com",
            "password": "NewPass456"
        }
    )

    assert new_login.status_code == 200

    old_login = client.post(
        "/auth/login",
        json={
            "email": "sara@example.com",
            "password": "TestPass123"
        }
    )

    assert old_login.status_code == 401


# Reject password change with the wrong current password
def test_change_password_rejects_wrong_current_password(client):
    headers = _register_and_login(client)

    response = client.patch(
        "/auth/password",
        headers=headers,
        json={
            "current_password": "WrongPass123",
            "new_password": "NewPass456"
        }
    )

    assert response.status_code == 400

    login_response = client.post(
        "/auth/login",
        json={
            "email": "sara@example.com",
            "password": "TestPass123"
        }
    )

    assert login_response.status_code == 200





def test_user_cannot_view_another_users_application(client):
    owner_headers = _register_and_login(
        client,
        email="view-owner@example.com"
    )
    application = _create_application(client, owner_headers)

    other_headers = _register_and_login(
        client,
        email="view-other@example.com"
    )

    response = client.get(
        f"/job-applications/{application['id']}",
        headers=other_headers
    )

    assert response.status_code == 404





def test_change_password_rejects_short_new_password(client):
    headers = _register_and_login(
        client,
        email="short-newpass@example.com"
    )

    response = client.patch(
        "/auth/password",
        headers=headers,
        json={
            "current_password": "TestPass123",
            "new_password": "1234"
        }
    )

    assert response.status_code == 422

    login_response = client.post(
        "/auth/login",
        json={
            "email": "short-newpass@example.com",
            "password": "TestPass123"
        }
    )

    assert login_response.status_code == 200




def test_update_job_application_salary(client):
    headers = _register_and_login(client)
    application = _create_application(client, headers)

    response = client.patch(
        f"/job-applications/{application['id']}",
        headers=headers,
        json={"salary": 45000}
    )

    assert response.status_code == 200
    assert response.json()["salary"] == 45000
    assert response.json()["company"] == "Google"




def test_create_job_application_with_salary(client):
    headers = _register_and_login(client)

    response = client.post(
        "/job-applications/",
        headers=headers,
        json={
            "company": "Google",
            "job_title": "Data Analyst",
            "job_url": "https://careers.google.com/",
            "notes": "Applied through website",
            "salary": 45000
        }
    )

    assert response.status_code == 201
    assert response.json()["salary"] == 45000
    assert response.json()["company"] == "Google"




def test_create_job_application_without_optional_fields(client):
    headers = _register_and_login(client)

    response = client.post(
        "/job-applications/",
        headers=headers,
        json={
            "company": "Google",
            "job_title": "Data Analyst"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["job_url"] is None
    assert data["notes"] is None



def test_update_job_application_rejects_negative_salary(client):
    headers = _register_and_login(client)
    application = _create_application(client, headers)

    response = client.patch(
        f"/job-applications/{application['id']}",
        headers=headers,
        json={"salary": -100}
    )

    assert response.status_code == 422







def test_filter_job_applications_by_status(client):
    headers = _register_and_login(client)

    google_app = _create_application(client, headers, company="Google")
    _create_application(client, headers, company="Microsoft")

    update_response = client.patch(
        f"/job-applications/{google_app['id']}",
        headers=headers,
        json={"status": "interview"}
    )
    assert update_response.status_code == 200

    response = client.get(
        "/job-applications/?status=interview",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Google"
    assert data[0]["status"] == "interview"