def test_health(client):
    assert client.get("/health").status_code == 200

def test_register_and_login(client):
    r = client.post("/register", json={"email": "a@b.com", "password": "password@123"})
    assert r.status_code == 201
    r = client.post("/login", data={"username": "a@b.com", "password": "password@123"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_wrong_password_reject(client):
    client.post("/register", json={"email": "a@b.com", "password": "password@123"})
    r = client.post("/login", data={"username": "a@b.com", "password": "wrong"})
    assert r.status_code == 401

def test_staff_cannot_create_product(client):
    client.post("/register", json={"email": "a@b.com", "password": "password@123"})
    login = client.post("/login", data={"username": "a@b.com", "password": "password@123"})
    token = login.json()["access_token"]

    r = client.post("/products", json={"name": "pen", "price": 10, "stock": 20}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code ==403

def test_create_product_without_token_returns_401(client):
    r = client.post("/products", json={"name": "pen", "price": 10, "stock": 20})
    assert r.status_code == 401

from conftest import make_user

def test_two_item_order_reduces_stock_from_both(client):
    admin = make_user(client, "a@x.com", role="admin")

    r = client.post("/products", json={"name": "A", "price": 1, "stock": 10}, headers=admin)
    print(r.status_code, r.json())
    a = r.json()["id"]
    b = client.post("/products", json={"name": "B", "price": 2, "stock": 10}, headers=admin).json()["id"]

    r = client.post("/orders", json={"items": [
        {"product_id": a, "quantity": 2},
        {"product_id": b, "quantity": 3},
    ]},
    headers=admin,
    )
    assert r.status_code == 201

    stocks = {p["id"]: p["stock"] for p in client.get("/products").json()}
    assert stocks[a]==8
    assert stocks[b]==7

from repository import get_connection

def test_oversell_returns_409_and_rolls_back(client):
    admin = make_user(client, "a@b.com", role="admin")
    r = client.post("/products", json={"name": "A", "price": 1, "stock": 5}, headers=admin)
    pid = r.json()["id"]
    r = client.post(
        "/orders",
        json={"items": [{"product_id": pid, "quantity": 99}]},
        headers=admin,
    )
    assert r.status_code == 409

    assert client.get("/products").json()[0]["stock"] == 5
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM orders"
            )
            assert cur.fetchone()[0] == 0

def test_delete_product_in_order_returns_409(client):
    admin = make_user(client, "a@b.com", role="admin")
    r = client.post("/products", json={"name": "A", "price": 1, "stock": 5}, headers=admin)
    pid=r.json()["id"]
    client.post("/orders", json={"items": [{"product_id": pid, "quantity": 1}]}, headers=admin)
    assert client.delete(f"/products/{pid}", headers=admin).status_code == 409