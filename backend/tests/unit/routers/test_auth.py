import time


def test_login_ok(client):
    # When: Default user logs in
    response = client.post(
        "/api/login",
        data={"username": "test", "password": "test"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    r = response.json()
    # Then: The response contains access_token, refresh_token and token_type
    assert "access_token" in r
    assert "refresh_token" in r
    assert "token_type" in r
    assert r["token_type"] == "Bearer"


def test_login_wrong_password(client):
    # When: Default user logs in with wrong password
    response = client.post(
        "/api/login",
        data={"username": "test", "password": "wrong"},
    )
    # Then: The response status code is 401
    assert response.status_code == 401


def test_login_wrong_username(client):
    # When: Default user logs in with wrong password
    response = client.post(
        "/api/login",
        data={"username": "admin@test", "password": "test"},
    )
    # Then: The response status code is 401
    assert response.status_code == 401


def test_logout(client, tokens):
    # When: Default user logs out
    response = client.post(
        "/api/logout",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200


def test_refresh_token(client, tokens):
    # Wait for 1 second
    time.sleep(1)
    # When: Default user refreshes token
    response = client.post(
        "/api/refresh-token",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    r = response.json()
    # Then: The response contains access_token, refresh_token and token_type
    assert "access_token" in r
    assert "refresh_token" in r
    assert "token_type" in r
    assert r["token_type"] == "Bearer"
    assert r["access_token"] != tokens["access_token"]
    assert r["refresh_token"] != tokens["refresh_token"]


def test_change_password(client, tokens):
    # When: Default user changes password
    response = client.post(
        "/api/change-password",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"old_password": "test", "new_password": "new_test"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    # When: Default user logs in with new password
    response = client.post(
        "/api/login",
        data={"username": "test", "password": "new_test"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    # Clean up
    assert (
        200
        == client.post(
            "/api/change-password",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"old_password": "new_test", "new_password": "test"},
        ).status_code
    )
