def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_ticket(client):
    resp = client.post(
        "/api/tickets",
        json={"title": "VPN keeps dropping", "priority": "urgent", "assignee": "sam"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["title"] == "VPN keeps dropping"
    assert body["priority"] == "urgent"
    assert body["status"] == "open"


def test_create_ticket_rejects_bad_priority(client):
    resp = client.post(
        "/api/tickets", json={"title": "bad one", "priority": "whenever"}
    )
    assert resp.status_code == 422


def test_list_tickets(client, sample_ticket):
    resp = client.get("/api/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(t["id"] == sample_ticket["id"] for t in data)


def test_get_single_ticket(client, sample_ticket):
    resp = client.get(f"/api/tickets/{sample_ticket['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_ticket["id"]


def test_get_missing_ticket_returns_404(client):
    resp = client.get("/api/tickets/999999")
    assert resp.status_code == 404


def test_update_ticket_status(client, sample_ticket):
    resp = client.put(
        f"/api/tickets/{sample_ticket['id']}",
        json={"status": "in_progress", "assignee": "dana"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_progress"
    assert body["assignee"] == "dana"


def test_update_rejects_bad_status(client, sample_ticket):
    resp = client.put(
        f"/api/tickets/{sample_ticket['id']}", json={"status": "not_a_status"}
    )
    assert resp.status_code == 422


def test_delete_ticket(client, sample_ticket):
    tid = sample_ticket["id"]
    resp = client.delete(f"/api/tickets/{tid}")
    assert resp.status_code == 204
    assert client.get(f"/api/tickets/{tid}").status_code == 404


def test_filter_by_status(client):
    client.post("/api/tickets", json={"title": "open one"})
    created = client.post("/api/tickets", json={"title": "closed one"}).json()
    client.put(f"/api/tickets/{created['id']}", json={"status": "closed"})

    resp = client.get("/api/tickets", params={"status": "closed"})
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert titles == ["closed one"]


def test_stats_summary(client):
    client.post("/api/tickets", json={"title": "a", "priority": "low"})
    client.post("/api/tickets", json={"title": "b", "priority": "high"})
    resp = client.get("/api/tickets/stats/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert body["by_status"]["open"] == 2
    assert body["by_priority"]["low"] == 1
    assert body["by_priority"]["high"] == 1


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "# HELP" in resp.text
