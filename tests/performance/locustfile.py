"""Performance tests for GUDLFT.

Run the server first (flask --app server run), then:
    locust -f tests/performance/locustfile.py --host http://127.0.0.1:5000

Targets from the specifications (6 users by default):
    - loading the competitions list: < 5 seconds
    - updating the points total: < 2 seconds
"""
import random

from locust import HttpUser, between, task

CLUBS = [
    ("Simply Lift", "john@simplylift.co"),
    ("Iron Temple", "admin@irontemple.com"),
    ("She Lifts", "kate@shelifts.co.uk"),
]
FUTURE_COMPETITION = "Winter Challenge"

COMPETITIONS_LIST_MAX_TIME = 5
POINTS_UPDATE_MAX_TIME = 2


class SecretaryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.club_name, self.club_email = random.choice(CLUBS)
        self.client.post("/showSummary", data={"email": self.club_email})

    @task(3)
    def competitions_list(self):
        with self.client.post("/showSummary", data={"email": self.club_email},
                              name="/showSummary (competitions list)",
                              catch_response=True) as response:
            if response.elapsed.total_seconds() > COMPETITIONS_LIST_MAX_TIME:
                response.failure(f"Competitions list took more than {COMPETITIONS_LIST_MAX_TIME}s")

    @task(2)
    def booking_page(self):
        self.client.get(f"/book/{FUTURE_COMPETITION}/{self.club_name}",
                        name="/book/[competition]/[club]")

    @task(1)
    def purchase_places(self):
        with self.client.post("/purchasePlaces",
                              data={"competition": FUTURE_COMPETITION,
                                    "club": self.club_name,
                                    "places": "1"},
                              name="/purchasePlaces (points update)",
                              catch_response=True) as response:
            if response.elapsed.total_seconds() > POINTS_UPDATE_MAX_TIME:
                response.failure(f"Points update took more than {POINTS_UPDATE_MAX_TIME}s")

    @task(2)
    def points_board(self):
        self.client.get("/pointsBoard")

    @task(1)
    def index(self):
        self.client.get("/")
