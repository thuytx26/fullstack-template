from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


client = TestClient(app)


response = client.post(
    f"{settings.API_V1_STR}/login/access-token",
    data={
        "username": settings.FIRST_SUPERUSER_NAME, 
        "password": settings.FIRST_SUPERUSER_PASSWORD
        },
)

response = response.json()
print(response['access_token'])
# response = dict(response.text)
# print(response['access_token'])