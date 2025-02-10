def test_register_is_good(client):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    username = "stringerrrrrrrrrrrrr"
    password = "string3R_"
    json_data = {
        "username": username,
        "password": password,
    }
    response = client.post("/auth/register", json=json_data, headers=headers)
    assert response.status_code == 200
    new_user = response.json()
    assert new_user["username"] == username
