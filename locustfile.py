from locust import HttpLocust, TaskSet, between, task

def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def logout(l):
    l.client.post("/logout", {"username":"ellen_key", "password":"education"})

def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class InnerUserBehaviour(TaskSet):
    @task
    def new_thread(self):
        pass

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1, InnerUserBehaviour: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)