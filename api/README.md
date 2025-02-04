# FastAPI JWT Auth API

### Summary:

FastAPI, Postgres, Sqlalchemy, Pydantic v2, Docker
API example with JWT Authentication.

### Requirements:
```
docker
```
-   В директории проекта выполнить:

``` bash
docker-compose up -d api
```

### Run:

```bash
cp config/.env.example config/.env
docker compose up --build
```

### Docs:


OpenAPI: [спецификация API](http://localhost:8000/docs)

Postman: postman_collection.json in the project root.


### Endpoints:

```http request
POST   /auth/token                       # token get
POST   /auth/refresh                     # token refresh

POST   /users                            # user create
GET    /users                            # user get
PATCH  /users                            # user update
DELETE /users                            # user delete

GET    /users/admin                      # user list (admin)

GET    /                                 # health check
```

### Example Requests/Responses:

- Авторизация
#### Request:

```http request
POST /auth/login

Body:
{
    "username": "user",
    "password": "123456"
}
```

#### Response:
```json
{
    "access_token": "<access_token_string>",
    "refresh_token": "<refresh_token_string>",
    "token_type": "bearer"
}
```

#### Request:
```http request
GET /users
Headers:
Authorization: Bearer <access_token_string>
```

#### Response:
```json
{
    "id": 1,
    "username": "user",
    "email": "user@test.com",
    "first_name": "fname",
    "last_name": "lname",
    "active": true,
    "role": "user",
    "create_date": "2023-11-17T13:23:45.737500",
    "update_date": "2023-11-17T13:23:45.737500"
}
```

- Обновление сессии
#### Request:
```http request
POST /auth/refresh

{
    "refresh_token": "<refresh_token_string>"
}
```

#### Response:
```json
{
    "access_token": "<access_token_string>",
    "refresh_token": "<refresh_token_string>",
    "token_type": "bearer"
}
```

### Database Tables:

```json
{
  "Base (Abstract)": {
    "id": "int",
    "create_date": "datetime",
    "update_date": "datetime"
  },
  "User": {
    "username": "str",
    "password": "str", // pragma: allowlist-secret
    "email": "str",
    "first_name": "str",
    "last_name": "str",
    "active": "bool",
    "role": "enum(str)",
    "password_timestamp": "float" // pragma: allowlist-secret
  }
}
```

### Migration:

``` bash
docker exec api alembic revision --autogenerate -m "description"
docker exec api alembic upgrade head
```
