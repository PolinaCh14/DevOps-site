from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project, Status, ProjectSkill
from skill.models import Skill
from users.models import Role
import datetime

User = get_user_model()

class ProjectTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "testpassword123"
        role = Role.objects.create(id=2)
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password=self.password,
            role_id=role.id  # або інший відповідний ID
        )
        self.status = Status.objects.create(status="Відкритий")
        self.skill = Skill.objects.create(skill="Python")

        self.project = Project.objects.create(
            user=self.user,
            status=self.status,
            name="Test Project",
            description="Test Description",
            execution=10,
            end_at=datetime.date.today() + datetime.timedelta(days=30),
            price=1000.00
        )
        ProjectSkill.objects.create(id_project=self.project, id_skill=self.skill)

    def test_users_projects_view(self):
        self.client.login(email=self.user.email, password=self.password)
        response = self.client.get(reverse('projects:user_projects'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")

    def test_users_project_view(self):
        self.client.login(email=self.user.email, password=self.password)
        response = self.client.get(reverse('projects:user_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.description)

    def test_create_project_view_get(self):
        self.client.login(email=self.user.email, password=self.password)
        response = self.client.get(reverse('projects:create_project'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Створити")

    def test_project_model_str_fields(self):
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.status.status, "Відкритий")

    def test_project_delete_view(self):
        self.client.login(email=self.user.email, password=self.password)
        response = self.client.post(reverse('projects:project_delete', args=[self.project.id]))
        self.assertEqual(response.status_code, 302)  # редірект
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

