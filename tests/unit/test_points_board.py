def test_points_board_is_public(client):
    response = client.get("/pointsBoard")
    assert response.status_code == 200


def test_points_board_lists_every_club_with_points(client):
    response = client.get("/pointsBoard")
    assert b"<td>Club A</td>" in response.data
    assert b"<td>20</td>" in response.data
    assert b"<td>Club B</td>" in response.data
    assert b"<td>4</td>" in response.data


def test_points_board_is_read_only(client):
    response = client.post("/pointsBoard")
    assert response.status_code == 405
