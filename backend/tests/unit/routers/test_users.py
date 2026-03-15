from core.users.user_model import User, UserHeader
from ampf.testing import ApiTestClient


def test_get_all(client: ApiTestClient):
    # Given: An initlialised storage with default user
    # When: I get all chat session
    r = client.get_typed_list("/api/users", 200, UserHeader)
    # Then: I get only default user
    assert 1 == len(r)


def test_post_get_put_delete(client: ApiTestClient):
    # POST
    user = User(username="marcin.leliwa@gmail.com", email="marcin.leliwa@gmail.com")
    client.post("/api/users", 200, json=user)

    # GET
    r = client.get_typed(f"/api/users/{user.username}", 200, User)
    assert user.username == r.username

    # PUT
    user.email = "marcin.leliwa2@gmail.com"
    r = client.put(f"/api/users/{user.username}", 200, json=user)
    r = client.get_typed(f"/api/users/{user.username}", 200, User)
    assert user.email == r.email

    # DELETE
    client.delete(f"/api/users/{user.username}", 200)
    client.get(f"/api/users/{user.username}", 404)



def test_add_user_without_password(client: ApiTestClient):
    # Given: An user without password
    user = User(username="jasio", email="jasio.fasola@wp.pl")
    client.post("/api/users", 200, json=user)
    # When: Log in
    response = client.post("/api/login", data={"username": "jasio", "password": ""})
    # Then: It is forbidden (response 4xx)
    assert 400 <= response.status_code <= 499
