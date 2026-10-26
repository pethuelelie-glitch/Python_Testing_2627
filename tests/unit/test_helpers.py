import server


def test_load_clubs_returns_list_of_clubs():
    clubs = server.loadClubs()
    assert isinstance(clubs, list)
    assert all("email" in club and "points" in club for club in clubs)


def test_load_competitions_returns_list_of_competitions():
    competitions = server.loadCompetitions()
    assert isinstance(competitions, list)
    assert all("date" in comp and "numberOfPlaces" in comp for comp in competitions)


def test_is_past_competition_true_for_past_date():
    assert server.isPastCompetition({"date": "2020-03-27 10:00:00"}) is True


def test_is_past_competition_false_for_future_date():
    assert server.isPastCompetition({"date": "2099-01-01 10:00:00"}) is False
