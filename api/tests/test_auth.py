# import random
# import string

# import pytest


# @pytest.mark.asyncio
# async def test_1_registration(async_client):
#     data = {"username": "whisperteam", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()


# @pytest.mark.asyncio
# async def test_2_registration_wrong_username_format(async_client):
#     data = {"username": "whisper-team", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422, response.json()


# @pytest.mark.asyncio
# async def test_3_registration_password_without_spec_symbols(async_client):
#     data = {"username": "whisperteam1", "password": "String123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422, response.json()


# @pytest.mark.asyncio
# async def test_4_registration_password_without_numbers(async_client):
#     data = {"username": "whisperteam2", "password": "String@"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422, response.json()


# @pytest.mark.asyncio
# async def test_5_registration_password_without_latin_letters(async_client):
#     data = {"username": "whisperteam2", "password": "@123456678"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422, response.json()


# @pytest.mark.asyncio
# async def test_6_registration_password_less_six_symbols(async_client):
#     data = {"username": "whisperteam", "password": "Str@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_7_registration_password_without_uppercase_letters(async_client):
#     data = {"username": "whisperteam", "password": "string@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_8_registration_password_without_lowercase_letters(async_client):
#     data = {"username": "whisperteam", "password": "STRING@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_9_registration_username_without_letters(async_client):
#     data = {"username": "", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_10_registration_username_less_5_letters(async_client):
#     data = {"username": "whis", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_11_registration_username_less_5_letters(async_client):
#     data = {"username": "whis", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_12_registration_username_greater_64_letters(async_client):
#     data = {"username": "".join(random.choices(string.ascii_letters, k=65)), "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_13_registration_password_greater_256_letters(async_client):
#     data = {"username": "whisperteam", "password": "".join(random.choices(string.digits, k=256))}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 422


# @pytest.mark.asyncio
# async def test_14_login(async_client):
#     data = {"username": "whisperteam", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()

#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 200 and "access_token" in response.json()


# @pytest.mark.asyncio
# async def test_15_login_unauthorized(async_client):
#     data = {"username": "whisperteam", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()

#     data = {"username": "whisperteamcoursework", "password": "String@123"}

#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 401


# @pytest.mark.asyncio
# async def test_16_refresh(async_client):
#     data = {"username": "whisperteam", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()
#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 200 and "refresh_token" in response.json()
#     data = {"refresh_token": response.json()["refresh_token"]}
#     response = await async_client.post("/auth/refresh", json=data)
#     assert response.status_code == 200 and "refresh_token" in response.json()


# @pytest.mark.asyncio
# async def test_17_refresh_invalid_token(async_client):
#     data = {"username": "whisperteam", "password": "String@123"}
#     response = await async_client.post("/auth/register", json=data)
#     assert response.status_code == 201 or response.status_code == 409, response.json()
#     response = await async_client.post("/auth/login", json=data)
#     assert response.status_code == 200 and "refresh_token" in response.json()
#     data = {"refresh_token": response.json()["refresh_token"] + "1"}
#     response = await async_client.post("/auth/refresh", json=data)
#     assert response.status_code == 401
