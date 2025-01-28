# Create user
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "stringer",
  "password": "string3R_"
}'

# Get the token
echo
ACCESS_TOKEN=$(curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "stringer",
  "password": "string3R_"
}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Activate account (however that requeries header...)
echo
curl -X 'PATCH' \
  'http://localhost:8000/auth/patch' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{
  "can_interact": true
}'

echo -e "\n\nAccess token is ${ACCESS_TOKEN}"
