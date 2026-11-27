def make_product(client, name="Camiseta", price="49.90", stock=10):
    r = client.post("/products", json={"name": name, "price": price, "stock": stock})
    assert r.status_code == 201
    return r.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_product_crud(client):
    p = make_product(client)
    assert client.get(f"/products/{p['id']}").json()["name"] == "Camiseta"

    r = client.patch(f"/products/{p['id']}", json={"stock": 3})
    assert r.status_code == 200 and r.json()["stock"] == 3

    assert len(client.get("/products", params={"search": "cami"}).json()) == 1
    assert client.get("/products", params={"search": "xyz"}).json() == []

    assert client.delete(f"/products/{p['id']}").status_code == 204
    assert client.get(f"/products/{p['id']}").status_code == 404


def test_product_validation(client):
    r = client.post("/products", json={"name": "X", "price": "-1", "stock": 1})
    assert r.status_code == 422


def test_create_order_updates_stock_and_total(client):
    p = make_product(client, price="10.00", stock=5)
    r = client.post(
        "/orders",
        json={"customer_email": "a@b.com", "items": [{"product_id": p["id"], "quantity": 2}]},
    )
    assert r.status_code == 201
    order = r.json()
    assert float(order["total"]) == 20.0
    assert order["status"] == "PENDING"
    assert client.get(f"/products/{p['id']}").json()["stock"] == 3


def test_order_insufficient_stock(client):
    p = make_product(client, stock=1)
    r = client.post(
        "/orders",
        json={"customer_email": "a@b.com", "items": [{"product_id": p["id"], "quantity": 2}]},
    )
    assert r.status_code == 409
    assert client.get(f"/products/{p['id']}").json()["stock"] == 1


def test_order_unknown_product(client):
    r = client.post(
        "/orders",
        json={"customer_email": "a@b.com", "items": [{"product_id": 999, "quantity": 1}]},
    )
    assert r.status_code == 404


def test_cancel_order_restores_stock(client):
    p = make_product(client, stock=5)
    order = client.post(
        "/orders",
        json={"customer_email": "a@b.com", "items": [{"product_id": p["id"], "quantity": 4}]},
    ).json()

    r = client.post(f"/orders/{order['id']}/cancel")
    assert r.status_code == 200 and r.json()["status"] == "CANCELLED"
    assert client.get(f"/products/{p['id']}").json()["stock"] == 5
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 409


def test_list_orders_by_customer(client):
    p = make_product(client, stock=10)
    for email in ("a@b.com", "c@d.com"):
        client.post(
            "/orders",
            json={"customer_email": email, "items": [{"product_id": p["id"], "quantity": 1}]},
        )
    r = client.get("/orders", params={"customer_email": "a@b.com"})
    assert len(r.json()) == 1
