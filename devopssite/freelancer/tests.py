from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Role
from .models import Freelancer, Portfolio, FreelancerStatus, FreelancerSkill
from skill.models import Skill
from project.models import Project, Status as ProjectStatus
from rating.models import Rating


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


class FreelancerFilteringTests(TestCase):
    list_urls = ('freelancers:freelancer_list', 'adminp:freelancer_list_a')

    def setUp(self):
        self.client = Client()
        role = Role.objects.create(role='freelancer')
        self.status_active = FreelancerStatus.objects.create(status='active')
        self.status_inactive = FreelancerStatus.objects.create(status='inactive')

        self.alpha = self.create_freelancer(
            'alpha@example.com', 'Alpha', 'One', '1000000001', 2, self.status_active
        )
        self.bravo = self.create_freelancer(
            'bravo@example.com', 'Bravo', 'Two', '1000000002', 5, self.status_active
        )
        self.charlie = self.create_freelancer(
            'charlie@example.com', 'Charlie', 'Three', '1000000003', 1, self.status_inactive
        )
        self.delta = self.create_freelancer(
            'delta@example.com', 'Delta', 'Four', '1000000004', 4, self.status_inactive
        )

        self.aws = Skill.objects.create(skill='AWS')
        self.docker = Skill.objects.create(skill='Docker')
        self.python = Skill.objects.create(skill='Python')
        self.add_skills(self.alpha, self.aws, self.python)
        self.add_skills(self.bravo, self.docker)
        self.add_skills(self.charlie, self.aws, self.docker)
        self.add_skills(self.delta, self.python)

        project_status = ProjectStatus.objects.create(status='active')
        self.project = Project.objects.create(
            user=self.alpha.id_user,
            status=project_status,
            name='Rating project',
            description='Project used for freelancer rating tests',
        )
        self.add_rating(self.alpha, '4.00')
        self.add_rating(self.alpha, '3.00')
        self.add_rating(self.bravo, '5.00')
        self.add_rating(self.delta, '2.50')

    def create_freelancer(self, email, name, surname, phone, experience, status):
        user = User.objects.create_user(
            email=email,
            password='test123',
            role=Role.objects.get(role='freelancer'),
            name=name,
            surname=surname,
            phone=phone,
        )
        return Freelancer.objects.create(
            id_user=user,
            id_status=status,
            experience=experience,
        )

    @staticmethod
    def add_skills(freelancer, *skills):
        FreelancerSkill.objects.bulk_create([
            FreelancerSkill(id_freelancer=freelancer, id_skill=skill)
            for skill in skills
        ])

    def add_rating(self, freelancer, value):
        Rating.objects.create(
            id_evaluates=freelancer.id_user,
            id_appraiser=self.alpha.id_user,
            id_project=self.project,
            rating=value,
        )

    def freelancer_names(self, response):
        return [
            freelancer.id_user.name
            for freelancer in response.context['freelancers']
        ]

    def request_lists(self, params=None):
        return [
            self.client.get(reverse(url_name), params or {})
            for url_name in self.list_urls
        ]

    def test_skill_controls_use_checkboxes_and_ukrainian_mode_labels_on_both_pages(self):
        for response in self.request_lists():
            self.assertContains(response, 'type="checkbox"', html=False)
            self.assertContains(response, 'name="skill"', html=False)
            self.assertContains(response, 'class="skill-picker-options"', html=False)
            self.assertContains(response, 'Обрано: 0', html=False)
            self.assertContains(response, 'Будь-яка з вибраних', html=False)
            self.assertContains(response, 'Усі вибрані', html=False)
            self.assertContains(response, 'name="skill_mode"', html=False)
            self.assertContains(response, 'name="sort_by"', html=False)
            self.assertNotContains(response, '<details', html=False)
            self.assertNotContains(response, 'data-selected-skills', html=False)
            self.assertNotContains(response, 'skill-chip-remove', html=False)
            self.assertNotContains(response, 'Видалити навичку', html=False)
            self.assertNotContains(response, 'ANY')
            self.assertNotContains(response, 'ALL')
            self.assertEqual(response.context['skill_mode'], 'any')

    def test_selected_filters_are_preserved_in_both_forms(self):
        params = {
            'name': 'Alpha',
            'status': self.status_active.id,
            'skill': [self.aws.id, self.docker.id],
            'skill_mode': 'all',
            'experience': '3',
            'experience_filter': 'gte',
            'rating': '4.0',
            'rating_filter': 'gte',
            'sort_by': 'rating_desc',
        }
        for url_name in self.list_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name), params)
                self.assertEqual(response.context['selected_skill_ids'], [
                    str(self.aws.id), str(self.docker.id)
                ])
                self.assertEqual(response.context['skill_mode'], 'all')
                self.assertContains(response, 'value="Alpha"', html=False)
                self.assertContains(response, f'value="{self.aws.id}"', html=False)
                self.assertContains(response, f'value="{self.docker.id}"', html=False)
                rendered_form = response.content.decode()
                self.assertRegex(
                    rendered_form,
                    rf'id="freelancer-skill-{self.aws.id}"\s+type="checkbox"\s+name="skill"\s+value="{self.aws.id}"\s+checked'
                )
                self.assertRegex(
                    rendered_form,
                    rf'id="freelancer-skill-{self.docker.id}"\s+type="checkbox"\s+name="skill"\s+value="{self.docker.id}"\s+checked'
                )
                self.assertContains(response, 'Обрано: 2', html=False)
                self.assertContains(response, 'value="all" selected', html=False)
                self.assertContains(response, 'name="experience" value="3"', html=False)
                self.assertContains(response, 'value="gte" selected', html=False)
                self.assertContains(response, 'name="rating" value="4.0"', html=False)
                self.assertContains(response, 'value="rating_desc" selected', html=False)
                self.assertContains(response, f'id="freelancer-skill-{self.aws.id}"', html=False)
                self.assertContains(response, f'id="freelancer-skill-{self.docker.id}"', html=False)

    def test_any_and_all_skill_matching_on_both_pages(self):
        for url_name in self.list_urls:
            with self.subTest(url_name=url_name, mode='any'):
                response = self.client.get(reverse(url_name), {
                    'skill': [self.aws.id, self.docker.id],
                    'skill_mode': 'any',
                })
                self.assertCountEqual(
                    self.freelancer_names(response), ['Alpha', 'Bravo', 'Charlie']
                )

            with self.subTest(url_name=url_name, mode='all'):
                response = self.client.get(reverse(url_name), {
                    'skill': [self.aws.id, self.docker.id],
                    'skill_mode': 'all',
                })
                self.assertEqual(self.freelancer_names(response), ['Charlie'])

    def test_multi_skill_filter_combines_with_status_and_experience(self):
        for url_name in self.list_urls:
            with self.subTest(url_name=url_name, filter='status'):
                response = self.client.get(reverse(url_name), {
                    'skill': [self.aws.id, self.docker.id],
                    'status': self.status_active.id,
                })
                self.assertCountEqual(self.freelancer_names(response), ['Alpha', 'Bravo'])

            with self.subTest(url_name=url_name, filter='experience'):
                response = self.client.get(reverse(url_name), {
                    'skill': [self.aws.id, self.docker.id],
                    'experience': 3,
                    'experience_filter': 'gte',
                })
                self.assertEqual(self.freelancer_names(response), ['Bravo'])

    def test_multi_skill_filter_combines_with_rating_filter_in_one_rating_query(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        for url_name in self.list_urls:
            with self.subTest(url_name=url_name):
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(reverse(url_name), {
                        'skill': [self.aws.id, self.docker.id],
                        'rating': '3.5',
                        'rating_filter': 'gte',
                    })
                self.assertCountEqual(self.freelancer_names(response), ['Alpha', 'Bravo'])
                rating_queries = [
                    query for query in queries.captured_queries
                    if '"rating"' in query['sql'].lower()
                ]
                self.assertEqual(len(rating_queries), 1)

    def test_experience_sorting_ascending_and_descending_on_both_pages(self):
        for url_name in self.list_urls:
            with self.subTest(url_name=url_name, direction='ascending'):
                response = self.client.get(reverse(url_name), {
                    'sort_by': 'experience_asc',
                })
                self.assertEqual(
                    self.freelancer_names(response), ['Charlie', 'Alpha', 'Delta', 'Bravo']
                )

            with self.subTest(url_name=url_name, direction='descending'):
                response = self.client.get(reverse(url_name), {
                    'sort_by': 'experience_desc',
                })
                self.assertEqual(
                    self.freelancer_names(response), ['Bravo', 'Delta', 'Alpha', 'Charlie']
                )

    def test_rating_sorting_keeps_unrated_freelancers_last_in_both_directions(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        for url_name in self.list_urls:
            for direction, expected in (
                ('rating_asc', ['Delta', 'Alpha', 'Bravo', 'Charlie']),
                ('rating_desc', ['Bravo', 'Alpha', 'Delta', 'Charlie']),
            ):
                with self.subTest(url_name=url_name, direction=direction):
                    with CaptureQueriesContext(connection) as queries:
                        response = self.client.get(reverse(url_name), {
                            'sort_by': direction,
                        })
                    self.assertEqual(self.freelancer_names(response), expected)
                    rating_queries = [
                        query for query in queries.captured_queries
                        if '"rating"' in query['sql'].lower()
                    ]
                    self.assertEqual(len(rating_queries), 1)

    def test_existing_single_value_filters_and_unsorted_default_are_preserved(self):
        for url_name in self.list_urls:
            with self.subTest(url_name=url_name, case='legacy filters'):
                response = self.client.get(reverse(url_name), {
                    'name': 'Alpha',
                    'status': self.status_active.id,
                    'skill': self.aws.id,
                    'experience': 2,
                    'experience_filter': 'eq',
                    'rating': '3.5',
                    'rating_filter': 'gte',
                })
                self.assertEqual(self.freelancer_names(response), ['Alpha'])

            with self.subTest(url_name=url_name, case='default ordering'):
                response = self.client.get(reverse(url_name))
                freelancers = response.context['freelancers']
                self.assertFalse(freelancers.query.order_by)
                self.assertCountEqual(
                    self.freelancer_names(response), ['Alpha', 'Bravo', 'Charlie', 'Delta']
                )


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
