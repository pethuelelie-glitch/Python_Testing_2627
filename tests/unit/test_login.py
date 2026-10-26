def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"secretary email" in response.data


def test_login_with_known_email_shows_summary(client):
    response = client.post("/showSummary", data={"email": "a@test.com"})
    assert response.status_code == 200
    assert b"Welcome, a@test.com" in response.data
    assert b"Points available: 20" in response.data


def test_login_with_unknown_email_shows_error(client):
    response = client.post("/showSummary", data={"email": "unknown@test.com"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"wasn&#39;t found" in response.data


def test_login_stores_club_in_session(client):
    client.post("/showSummary", data={"email": "a@test.com"})
    with client.session_transaction() as session:
        assert session["club"] == "Club A"


def test_logout_clears_session(logged_client):
    response = logged_client.get("/logout")
    assert response.status_code == 302
    with logged_client.session_transaction() as session:
        assert "club" not in session


def test_summary_hides_booking_link_for_past_competition(client):
    response = client.post("/showSummary", data={"email": "a@test.com"})
    assert b"/book/Future%20Comp/Club%20A" in response.data
    assert b"/book/Past%20Comp/Club%20A" not in response.data
