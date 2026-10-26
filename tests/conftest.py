import pytest

import server


@pytest.fixture(autouse=True)
def test_data(monkeypatch):
    """Replace the JSON data with fresh test data before each test."""
    clubs = [
        {"name": "Club A", "email": "a@test.com", "points": "20"},
        {"name": "Club B", "email": "b@test.com", "points": "4"},
    ]
    competitions = [
        {"name": "Future Comp", "date": "2099-06-01 10:00:00", "numberOfPlaces": "25"},
        {"name": "Small Comp", "date": "2099-07-01 10:00:00", "numberOfPlaces": "3"},
        {"name": "Past Comp", "date": "2020-03-27 10:00:00", "numberOfPlaces": "10"},
    ]
    monkeypatch.setattr(server, "clubs", clubs)
    monkeypatch.setattr(server, "competitions", competitions)
    monkeypatch.setattr(server, "bookings", {})
    return {"clubs": clubs, "competitions": competitions}


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    with server.app.test_client() as client:
        yield client


@pytest.fixture
def logged_client(client):
    """A client already logged in as Club A."""
    client.post("/showSummary", data={"email": "a@test.com"})
    return client
