def test_full_booking_flow_updates_points_board(client):
    # The secretary logs in and sees the bookable competition
    response = client.post("/showSummary", data={"email": "a@test.com"})
    assert b"Points available: 20" in response.data

    # Opens the booking page and buys 3 places
    response = client.get("/book/Future Comp/Club A")
    assert b"Places available: 25" in response.data
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Future Comp", "club": "Club A", "places": "3"},
    )
    assert b"Great-booking complete!" in response.data
    assert b"Points available: 17" in response.data
    assert b"Number of Places: 22" in response.data

    # The public points board shows the new balance
    response = client.get("/pointsBoard")
    assert b"<td>17</td>" in response.data

    # After logout, booking is no longer possible
    client.get("/logout")
    response = client.get("/book/Future Comp/Club A", follow_redirects=True)
    assert b"Please log in" in response.data


def test_refused_booking_keeps_data_unchanged_and_allows_retry(client):
    client.post("/showSummary", data={"email": "b@test.com"})

    # Club B only has 4 points: asking for 5 is refused
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Future Comp", "club": "Club B", "places": "5"},
    )
    assert b"enough points" in response.data
    assert b"<td>4</td>" in client.get("/pointsBoard").data

    # Retrying with a valid amount works
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Future Comp", "club": "Club B", "places": "4"},
    )
    assert b"Great-booking complete!" in response.data
    assert b"<td>0</td>" in client.get("/pointsBoard").data


def test_unknown_user_cannot_book_and_can_still_see_points(client):
    response = client.post("/showSummary", data={"email": "nobody@test.com"}, follow_redirects=True)
    assert b"wasn&#39;t found" in response.data

    response = client.get("/book/Future Comp/Club A", follow_redirects=True)
    assert b"Please log in" in response.data

    response = client.get("/pointsBoard")
    assert response.status_code == 200
    assert b"Club A" in response.data
