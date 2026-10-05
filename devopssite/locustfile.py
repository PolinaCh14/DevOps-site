from locust import HttpUser, task, between
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt

class FreelancerUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)

    def on_start(self):

        response = self.client.get("/users/login/")  # або просто "/"

        csrftoken = response.cookies.get("csrftoken")

        headers = {"X-CSRFToken": csrftoken}
        self.client.post(
            "/users/login/",
            data={
                "email": "polina.chernyshova@nure.ua",
                "password": "121212",
                "csrfmiddlewaretoken": csrftoken
            },
            headers=headers
        )

    @task(2)
    def view_freelancer_list(self):
        self.client.get("/freelancers/freelancer_list/")

    @task(1)
    def view_freelancer_list_and_detail(self):
        # Спершу отримуємо список фрілансерів
        response = self.client.get("/freelancers/freelancer_list/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Шукаємо перше посилання на фрілансера
        links = soup.select('a[href*="/freelancers/"]')

        if links:
            href = links[0].get('href')
            # Переходимо на сторінку фрілансера за цим посиланням
            self.client.get(href)

    @task(1)
    def create_portfolio(self):
        response = self.client.get("/freelancers/freelancer/portfolio/create/")
        csrftoken = response.cookies.get("csrftoken")
        headers = {"X-CSRFToken": csrftoken}
        self.client.post(
            "/freelancers/freelancer/portfolio/create/",
            data={
                "title": "Load Test Project",
                "description": "Created via locust",
                "photo": "https://example.com/photo.jpg",
                "url": "https://github.com/example",
                "csrfmiddlewaretoken": csrftoken,
            },
            headers=headers
        )

    @task(1)
    def update_portfolio_item(self):
        # Отримуємо список портфоліо, парсимо перший ID
        response = self.client.get("/freelancers/freelancer/portfolio/4/edit/")
        soup = BeautifulSoup(response.text, 'html.parser')
        edit_links = soup.select('a[href*="/update_portfolio_item/"]')
        if edit_links:
            update_url = edit_links[0].get('href')
            self.client.post(update_url, {
                "title": "Updated title",
                "description": "Updated description",
                "photo": "https://example.com/photo-updated.jpg",
                "url": "https://github.com/updated"
            })

