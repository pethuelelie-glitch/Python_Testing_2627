import pytest

import server


def purchase(client, places, competition="Future Comp", club="Club A"):
    return client.post(
        "/purchasePlaces",
        data={"competition": competition, "club": club, "places": places},
        follow_redirects=True,
    )


def test_purchase_deducts_places_and_points(logged_client, test_data):
    response = purchase(logged_client, "5")
    assert b"Great-booking complete!" in response.data
    assert test_data["competitions"][0]["numberOfPlaces"] == 20
    assert test_data["clubs"][0]["points"] == 15
    assert b"Points available: 15" in response.data


def test_purchase_requires_login(client, test_data):
    response = purchase(client, "1")
    assert b"Please log in" in response.data
    assert test_data["clubs"][0]["points"] == "20"


def test_purchase_for_another_club_is_refused(logged_client, test_data):
    response = purchase(logged_client, "1", club="Club B")
    assert b"Please log in" in response.data
    assert test_data["clubs"][1]["points"] == "4"


def test_purchase_unknown_competition_shows_error(logged_client):
    response = purchase(logged_client, "1", competition="Unknown Comp")
    assert b"Something went wrong" in response.data


@pytest.mark.parametrize("places", ["", "abc", "2.5"])
def test_purchase_with_invalid_number_shows_error(logged_client, places):
    response = purchase(logged_client, places)
    assert b"Please enter a valid number of places." in response.data


@pytest.mark.parametrize("places", ["0", "-5"])
def test_purchase_with_zero_or_negative_places_is_refused(logged_client, test_data, places):
    response = purchase(logged_client, places)
    assert b"greater than zero" in response.data
    assert test_data["competitions"][0]["numberOfPlaces"] == "25"
    assert test_data["clubs"][0]["points"] == "20"


def test_purchase_more_than_available_places_is_refused(logged_client, test_data):
    response = purchase(logged_client, "4", competition="Small Comp")
    assert b"Not enough places available" in response.data
    assert test_data["competitions"][1]["numberOfPlaces"] == "3"


def test_purchase_all_remaining_places_is_allowed(logged_client, test_data):
    response = purchase(logged_client, "3", competition="Small Comp")
    assert b"Great-booking complete!" in response.data
    assert test_data["competitions"][1]["numberOfPlaces"] == 0


def test_purchase_more_than_club_points_is_refused(client, test_data):
    client.post("/showSummary", data={"email": "b@test.com"})
    response = purchase(client, "5", club="Club B")
    assert b"enough points" in response.data
    assert test_data["clubs"][1]["points"] == "4"


def test_purchase_exactly_club_points_is_allowed(client, test_data):
    client.post("/showSummary", data={"email": "b@test.com"})
    response = purchase(client, "4", club="Club B")
    assert b"Great-booking complete!" in response.data
    assert test_data["clubs"][1]["points"] == 0


def test_purchase_more_than_12_places_is_refused(logged_client, test_data):
    response = purchase(logged_client, "13")
    assert b"more than 12 places" in response.data
    assert test_data["clubs"][0]["points"] == "20"


def test_purchase_12_places_is_allowed(logged_client):
    response = purchase(logged_client, "12")
    assert b"Great-booking complete!" in response.data


def test_purchase_cumulative_bookings_over_12_are_refused(logged_client):
    purchase(logged_client, "10")
    response = purchase(logged_client, "3")
    assert b"more than 12 places" in response.data
    assert server.bookings[("Future Comp", "Club A")] == 10


def test_purchase_past_competition_is_refused(logged_client, test_data):
    response = purchase(logged_client, "1", competition="Past Comp")
    assert b"already taken place" in response.data
    assert test_data["competitions"][2]["numberOfPlaces"] == "10"
