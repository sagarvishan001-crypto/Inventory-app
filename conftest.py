import os
from dotenv import load_dotenv

load_dotenv()
os.environ["APP_ENV"] = "test"

assert os.getenv("TEST_DB_NAME") and os.getenv("TEST_DB_NAME") != os.getenv("DB_NAME"), "TEST_DB_NAME must be set different than DB_NAME"

import pytest
from fastapi.testclient import TestClient
from db import get_connection
from main import app

@pytest.fixture(autouse=True)
def clean_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "TRUNCATE order_items, orders, products, users RESTART IDENTITY CASCADE"
            )
    yield

@pytest.fixture
def client():
    return TestClient(app)

def make_user(client, email, password="passwrod@123", role="staff"):
    client.post("/register", json={"email": email, "password": password})
    if role != "staff":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET role = %s where email = %s", (role, email)
                )
    r = client.post("/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}