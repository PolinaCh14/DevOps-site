from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Role
from .models import Freelancer, Portfolio, FreelancerStatus, FreelancerSkill
from skill.models import Skill


class FreelancerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        role = Role.objects.create(id=2)
        self.user = User.objects.create_user(email='freelancer@example.com', password='test123', role=role, name='First', surname='Last', phone='1234567890')
        self.status_active = FreelancerStatus.objects.create(status="active")
        self.client.login(email='freelancer@example.com', password='test123')

    def test_create_freelancer_profile(self):
        response = self.client.post(reverse('freelancers:create_freelancer_profile'), {
            'cv': 'My CV',
            'experience': 2,
            'status': self.status_active.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Freelancer.objects.filter(id_user=self.user).exists())

    def test_update_freelancer_profile(self):
        freelancer = Freelancer.objects.create(id_user=self.user, cv='Old CV', experience=1,
                                               id_status=self.status_active)
        skill = Skill.objects.create(skill='Python')

        response = self.client.post(reverse('freelancers:update_freelancer_profile'), {
            'cv': 'Updated CV',
            'experience': 3,
            'status': self.status_active.id,
            'skills': [skill.id],
        })

        freelancer.refresh_from_db()
        self.assertEqual(freelancer.cv, 'Updated CV')
        self.assertEqual(freelancer.experience, 3)
        self.assertEqual(freelancer.id_status.id, self.status_active.id)
        self.assertTrue(FreelancerSkill.objects.filter(id_freelancer=freelancer, id_skill=skill).exists())

    # def test_user_freelancer_detail_view(self):
    #     status = FreelancerStatus.objects.create(status='Active')
    #     Freelancer.objects.create(id_user=self.user, cv='Detailed CV', experience=4, id_status=status)
    #     response = self.client.get(reverse('freelancers:user_freelancer_detail'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Detailed CV')

    def test_freelancer_detail_view(self):
        status = FreelancerStatus.objects.create(status='Active')
        freelancer = Freelancer.objects.create(id_user=self.user, cv='My CV', experience=5, id_status=status)
        response = self.client.get(reverse('freelancers:freelancer_detail', args=[freelancer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My CV')


class PortfolioViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        role = Role.objects.create(id=2)
        self.user = User.objects.create_user(email='freelancer@example.com', password='test123', role=role,
                                             name='First', surname='Last', phone='1234567890')
        self.status_active = FreelancerStatus.objects.create(status="active")
        self.client.login(email='freelancer@example.com', password='test123')
        self.freelancer = Freelancer.objects.create(id_user=self.user, cv='CV', experience=3, id_status=self.status_active)

    def test_create_portfolio_item(self):
        response = self.client.post(reverse('freelancers:create_portfolio'), {
            'title': 'New Project',
            'description': 'Some desc',
            'photo': '',
            'url': 'http://example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Portfolio.objects.count(), 1)

    def test_update_portfolio_item(self):
        portfolio = Portfolio.objects.create(
            id_freelancer=self.freelancer,
            title='Old Title',
            description='Old desc',
            url='http://old.com'
        )
        response = self.client.post(reverse('freelancers:update_portfolio', args=[portfolio.id]), {
            'title': 'New Title',
            'description': 'New desc',
            'url': 'http://new.com'
        })
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.title, 'New Title')
        self.assertEqual(portfolio.url, 'http://new.com')

    def test_delete_portfolio_item(self):
        portfolio = Portfolio.objects.create(
            id_freelancer=self.freelancer,
            title='To be deleted',
            description='desc',
            url='http://url.com'
        )
        response = self.client.post(reverse('freelancers:delete_portfolio', args=[portfolio.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Portfolio.objects.filter(id=portfolio.id).exists())

    def test_get_user_portfolio_view(self):
        portfolio = Portfolio.objects.create(
            id_freelancer=self.freelancer,
            title='My Portfolio',
            description='My work',
            url='http://example.com'
        )
        response = self.client.get(reverse('freelancers:get_user_portfolio', args=[portfolio.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Portfolio')
