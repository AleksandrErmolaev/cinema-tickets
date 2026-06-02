from locust import HttpUser, task, between, tag
import random

class TicketUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.email = f"user_{random.randint(1, 100000)}@test.com"
        self.password = "testpass123"
        self.session_id = None
        
        resp = self.client.post("/register", json={
            "email": self.email,
            "password": self.password
        })
        if resp.status_code != 201:
            print(f"Registration failed: {resp.status_code}")
            self.stop(True)
            return
        
        resp = self.client.post("/login", json={
            "email": self.email,
            "password": self.password
        })
        if resp.status_code == 200:
            self.token = resp.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            try:
                resp_movies = self.client.get("/movies", headers=self.headers)
                if resp_movies.status_code == 200 and resp_movies.json():
                    movie_id = resp_movies.json()[0]["id"]
                    resp_showtimes = self.client.get(f"/showtimes/{movie_id}", headers=self.headers)
                    if resp_showtimes.status_code == 200 and resp_showtimes.json():
                        self.session_id = resp_showtimes.json()[0]["id"]
            except Exception:
                pass
            if not self.session_id:
                self.session_id = "test-session-1"
        else:
            self.token = None
            self.headers = {}
            self.stop(True)

    @tag("auth")
    @task(3)
    def register_login(self):
        email = f"load_user_{random.randint(1, 1000000)}@test.com"
        self.client.post("/register", json={
            "email": email,
            "password": "pass"
        }, name="/register")
        self.client.post("/login", json={
            "email": email,
            "password": "pass"
        }, name="/login")
    
    @tag("movies")
    @task(5)
    def get_movies(self):
        self.client.get("/movies", name="/movies", headers=self.headers)
    
    @tag("showtimes")
    @task(3)
    def get_showtimes(self):
        self.client.get("/showtimes/1", name="/showtimes/{movie_id}", headers=self.headers)
    
    @tag("bookings")
    @task(2)
    def create_booking(self):
        if not self.session_id:
            return
        data = {
            "session_id": self.session_id,
            "seat_numbers": [random.randint(1, 10) for _ in range(2)],
            "user_id": self.email
        }
        self.client.post("/bookings", json=data, name="/bookings", headers=self.headers)
    
    @tag("analytics")
    @task(1)
    def analytics(self):
        self.client.get("/analytics/health", name="/analytics/health", headers=self.headers)
    
    @tag("notifications")
    @task(1)
    def notification_health(self):
        self.client.get("/notify/health", name="/notify/health", headers=self.headers)
    
    @tag("profile")
    @task(2)
    def get_profile(self):
        if self.token:
            self.client.get("/profile", name="/profile", headers=self.headers)