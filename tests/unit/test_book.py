def test_book_page_for_valid_club_and_competition(logged_client):
    response = logged_client.get("/book/Future Comp/Club A")
    assert response.status_code == 200
    assert b"How many places?" in response.data


def test_book_requires_login(client):
    response = client.get("/book/Future Comp/Club A", follow_redirects=True)
    assert b"Please log in" in response.data


def test_book_for_another_club_is_refused(logged_client):
    response = logged_client.get("/book/Future Comp/Club B", follow_redirects=True)
    assert b"Please log in" in response.data


def test_book_unknown_competition_shows_error(logged_client):
    response = logged_client.get("/book/Unknown Comp/Club A")
    assert response.status_code == 200
    assert b"Something went wrong" in response.data


def test_book_past_competition_is_refused(logged_client):
    response = logged_client.get("/book/Past Comp/Club A")
    assert response.status_code == 200
    assert b"already taken place" in response.data
    assert b"How many places?" not in response.data
