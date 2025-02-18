# import pytest


# @pytest.mark.asyncio
# async def test_1_info(async_client):
#     data = {"username": "whisperteam", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()

#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 200 and "access_token" in response.json()

#     headers = {"Authorization": f"Bearer {response.json().get('access_token')}"}
#     response = await async_client.get("/auth/info", headers=headers)
#     assert response.status_code == 201, response.json()


# @pytest.mark.asyncio
# async def test_2_user_update(async_client):
#     data = {"username": "whisperteamf", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()

#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 200 and "access_token" in response.json()

#     headers = {"Authorization": f"Bearer {response.json().get('access_token')}"}
#     response = await async_client.get("/auth/info", headers=headers)
#     assert response.status_code == 200

#     ddata = {"user_id": response.json()["id"], "secret_admin_token": "verysecretadmintokenyeah"}
#     jdata = {"password": "QwErTy123@_", "can_interact": True}

#     response = await async_client.patch("/auth/patch", json=jdata, params=ddata)
#     assert response.status_code == 200

#     ddata = {"user_id": response.json()["id"], "secret_admin_token": "verysecretadmintokenyeah"}
#     jdata = {"password": "String@123", "can_interact": True}

#     response = await async_client.patch("/auth/patch", json=jdata, params=ddata)
#     assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_3_user_update_wrong_password(async_client):
#     data = {"username": "whisperteamcursework", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()

#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 200 and "access_token" in response.json(), response.json()

#     headers = {"Authorization": f"Bearer {response.json().get('access_token')}"}
#     response = await async_client.get("/auth/info", headers=headers)
#     assert response.status_code == 200

#     ddata = {"user_id": response.json()["id"], "secret_admin_token": "verysecretadmintokenyeah"}
#     jdata = {"password": "123456", "can_interact": True}

#     response = await async_client.patch("/auth/patch", json=jdata, params=ddata)
#     assert response.status_code == 422
