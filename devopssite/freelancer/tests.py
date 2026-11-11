import io
import json
import os
import tempfile
import zipfile
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, Role
from .models import Freelancer, Portfolio, FreelancerStatus, FreelancerSkill
from . import utils as resume_utils
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


def valid_resume_analysis():
    return {
        "summary": "Підсумок кандидата",
        "detected_skills": [{"name": "Python", "evidence": "Згадано Python."}],
        "strengths": [{"strength": "Послідовність", "evidence": "Описано досвід."}],
        "improvement_areas": [{"area": "Результати", "rationale": "Не наведено метрик."}],
        "recommendations": ["Додайте вимірювані результати."],
    }


def docx_bytes():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<document/>")
    return output.getvalue()


class MockDriveResponse:
    def __init__(self, content, mime, filename="", status=200, cookies=None):
        self.content = content
        self.status_code = status
        self.headers = {"Content-Type": mime}
        if filename:
            self.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        self.cookies = cookies or {}
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("sensitive provider detail")

    def iter_content(self, chunk_size):
        yield self.content

    def close(self):
        self.closed = True


class ResumeSchemaTests(TestCase):
    def test_valid_payload_has_exact_keys_and_trims_strings(self):
        payload = valid_resume_analysis()
        payload["summary"] = "  " + payload["summary"] + "  "
        payload["detected_skills"][0]["name"] = " Python "
        result = resume_utils.validate_structured_response(json.dumps(payload))
        self.assertEqual(set(result), {
            "summary", "detected_skills", "strengths",
            "improvement_areas", "recommendations",
        })
        self.assertEqual(result["summary"], "Підсумок кандидата")
        self.assertEqual(result["detected_skills"][0]["name"], "Python")
        self.assertNotIn("score", result)

    def test_boundary_lengths_and_maximum_item_counts_are_accepted(self):
        payload = {
            "summary": "x" * 1000,
            "detected_skills": [
                {
                    "name": f"{index}" + "n" * (100 - len(str(index))),
                    "evidence": "e" * 500,
                }
                for index in range(20)
            ],
            "strengths": [
                {"strength": f"s{i}" + "x" * 298, "evidence": "e" * 500}
                for i in range(10)
            ],
            "improvement_areas": [
                {"area": f"a{i}" + "x" * 298, "rationale": "r" * 500}
                for i in range(10)
            ],
            "recommendations": [f"{i}" + "r" * 499 for i in range(10)],
        }
        self.assertEqual(
            resume_utils.validate_structured_response(json.dumps(payload)),
            payload,
        )

    def test_empty_arrays_are_valid(self):
        payload = valid_resume_analysis()
        for key in ("detected_skills", "strengths", "improvement_areas", "recommendations"):
            payload[key] = []
        self.assertEqual(
            resume_utils.validate_structured_response(json.dumps(payload)),
            payload,
        )

    def test_invalid_json_and_exact_key_policy_are_rejected(self):
        valid = valid_resume_analysis()
        invalid_responses = [
            "{",
            json.dumps(valid) + " trailing",
            "```json\n" + json.dumps(valid) + "\n```",
            json.dumps(valid).replace('"summary":', '"extra": 1, "summary":', 1),
            '{"summary":"a","summary":"b","detected_skills":[],"strengths":[],'
            '"improvement_areas":[],"recommendations":[]}',
            json.dumps(valid).replace('"summary":', '"missing":', 1),
            json.dumps(valid).replace(
                json.dumps(valid["summary"]), "NaN"
            ),
        ]
        for raw in invalid_responses:
            with self.subTest(raw=raw[:40]):
                with self.assertRaises(resume_utils.InvalidStructuredResponse):
                    resume_utils.validate_structured_response(raw)

    def test_wrong_types_nested_keys_blank_and_control_characters_are_rejected(self):
        invalid_payloads = []
        for key, wrong in (
            ("summary", None),
            ("summary", 4),
            ("detected_skills", {}),
            ("strengths", [None]),
            ("improvement_areas", [{"area": "a", "rationale": "r", "extra": "x"}]),
            ("recommendations", [True]),
        ):
            payload = valid_resume_analysis()
            payload[key] = wrong
            invalid_payloads.append(payload)

        payload = valid_resume_analysis()
        payload["detected_skills"][0].pop("evidence")
        invalid_payloads.append(payload)
        payload = valid_resume_analysis()
        payload["summary"] = " \t "
        invalid_payloads.append(payload)
        payload = valid_resume_analysis()
        payload["summary"] = "contains\u0001control"
        invalid_payloads.append(payload)

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(resume_utils.InvalidStructuredResponse):
                    resume_utils.validate_structured_response(json.dumps(payload))

    def test_over_limit_values_and_duplicate_items_are_rejected(self):
        cases = []
        for key, value in (
            ("summary", "x" * 1001),
            ("detected_skills", [
                {"name": f"n{i}", "evidence": "e"} for i in range(21)
            ]),
            ("strengths", [
                {"strength": f"s{i}", "evidence": "e"} for i in range(11)
            ]),
            ("improvement_areas", [
                {"area": f"a{i}", "rationale": "r"} for i in range(11)
            ]),
            ("recommendations", [f"r{i}" for i in range(11)]),
        ):
            payload = valid_resume_analysis()
            payload[key] = value
            cases.append(payload)

        for key, item_key, maximum, other_key in (
            ("detected_skills", "name", 100, "evidence"),
            ("strengths", "strength", 300, "evidence"),
            ("improvement_areas", "area", 300, "rationale"),
        ):
            payload = valid_resume_analysis()
            payload[key] = [{item_key: "x" * (maximum + 1), other_key: "e"}]
            cases.append(payload)

        for key, item_key, other_key, maximum in (
            ("detected_skills", "name", "evidence", 500),
            ("strengths", "strength", "evidence", 500),
            ("improvement_areas", "area", "rationale", 500),
        ):
            payload = valid_resume_analysis()
            payload[key] = [{item_key: "x", other_key: "e" * (maximum + 1)}]
            cases.append(payload)

        payload = valid_resume_analysis()
        payload["recommendations"] = ["r" * 501]
        cases.append(payload)
        payload = valid_resume_analysis()
        payload["detected_skills"] = [
            {"name": " Python  Developer ", "evidence": "e"},
            {"name": "python developer", "evidence": "different"},
        ]
        cases.append(payload)
        payload = valid_resume_analysis()
        payload["strengths"] = [
            {"strength": "Strong delivery", "evidence": "e"},
            {"strength": " strong   delivery ", "evidence": "other"},
        ]
        cases.append(payload)
        payload = valid_resume_analysis()
        payload["improvement_areas"] = [
            {"area": "Results", "rationale": "r"},
            {"area": " results ", "rationale": "other"},
        ]
        cases.append(payload)
        payload = valid_resume_analysis()
        payload["recommendations"] = ["Improve CV", " improve   cv "]
        cases.append(payload)

        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaises(resume_utils.InvalidStructuredResponse):
                    resume_utils.validate_structured_response(json.dumps(payload))


class ResumeUtilityTests(TestCase):
    def test_drive_download_identifies_pdf_and_docx_and_sets_timeouts(self):
        cases = (
            (b"%PDF-1.7\ncontent", "application/pdf", "resume.pdf", ".pdf"),
            (
                docx_bytes(),
                resume_utils.DOCX_MIME,
                "resume.docx",
                ".docx",
            ),
        )
        for content, mime, filename, expected_suffix in cases:
            with self.subTest(expected_suffix=expected_suffix):
                response = MockDriveResponse(content, mime, filename)
                session = Mock()
                session.get.return_value = response
                with patch("freelancer.utils.requests.Session", return_value=session):
                    with tempfile_test_path() as destination:
                        suffix = resume_utils.download_from_google_drive(
                            "drive-id", destination
                        )
                self.assertEqual(suffix, expected_suffix)
                session.get.assert_called_once_with(
                    "https://drive.google.com/uc?export=download",
                    params={"id": "drive-id"},
                    stream=True,
                    timeout=(5, 30),
                )
                self.assertTrue(response.closed)
                session.close.assert_called_once()

    def test_download_warning_confirmation_is_protocol_not_retry(self):
        first = MockDriveResponse(
            b"", "application/octet-stream", cookies={"download_warning_xyz": "token"}
        )
        confirmed = MockDriveResponse(b"%PDF-1.7", "application/pdf")
        session = Mock()
        session.get.side_effect = [first, confirmed]
        with patch("freelancer.utils.requests.Session", return_value=session):
            with tempfile_test_path() as destination:
                suffix = resume_utils.download_from_google_drive("drive-id", destination)
        self.assertEqual(suffix, ".pdf")
        self.assertEqual(session.get.call_count, 2)
        self.assertEqual(session.get.call_args_list[1].kwargs["params"], {
            "id": "drive-id", "confirm": "token",
        })
        self.assertTrue(first.closed)
        self.assertTrue(confirmed.closed)

    def test_analysis_uses_validated_suffix_for_matching_extractor(self):
        payload = valid_resume_analysis()
        for extension, content in ((".pdf", b"%PDF-"), (".docx", docx_bytes())):
            with self.subTest(extension=extension):
                def download(_file_id, destination):
                    with open(destination, "wb") as file:
                        file.write(content)
                    return extension

                with patch("freelancer.utils.download_from_google_drive", side_effect=download), \
                        patch("freelancer.utils.read_file", return_value="sample resume") as reader, \
                        patch("freelancer.utils._analyze_text", return_value=payload):
                    result = resume_utils.analyze_resume(
                        "https://drive.google.com/file/d/file-id/view", 17
                    )
                self.assertTrue(reader.call_args.args[0].endswith(extension))
                self.assertEqual(result, payload)

    def test_drive_http_timeout_network_invalid_and_mismatched_content_stop(self):
        scenarios = (
            ("HTTP", MockDriveResponse(b"", "application/pdf", status=503)),
            ("timeout", requests.Timeout("private timeout detail")),
            ("network", requests.ConnectionError("private network detail")),
            ("html", MockDriveResponse(
                b"<!DOCTYPE html><html><body>Access denied</body></html>",
                "application/octet-stream",
            )),
            ("unsupported", MockDriveResponse(b"not a document", "text/plain", "resume.txt")),
            ("mismatch", MockDriveResponse(
                docx_bytes(), "application/pdf", "resume.pdf"
            )),
        )
        for label, outcome in scenarios:
            with self.subTest(label=label):
                session = Mock()
                if isinstance(outcome, Exception):
                    session.get.side_effect = outcome
                else:
                    session.get.return_value = outcome
                with patch("freelancer.utils.requests.Session", return_value=session), \
                        patch("freelancer.utils._analyze_text") as analyze:
                    with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                        resume_utils.analyze_resume(
                            "https://drive.google.com/file/d/file-id/view", 17
                        )
                expected = (
                    "resume_file_invalid"
                    if label in {"unsupported", "mismatch"}
                    else "resume_retrieval_failed"
                )
                self.assertEqual(raised.exception.code, expected)
                self.assertEqual(session.get.call_count, 1)
                analyze.assert_not_called()

    def test_invalid_reference_stops_before_drive(self):
        with patch("freelancer.utils.requests.Session") as session, \
                patch("freelancer.utils._analyze_text") as analyze:
            with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                resume_utils.analyze_resume("not a drive link", 1)
        self.assertEqual(raised.exception.code, "resume_reference_invalid")
        session.assert_not_called()
        analyze.assert_not_called()

    def test_extraction_exception_and_empty_text_stop_before_ai(self):
        for extracted, expected in (
            (ValueError("private parser exception"), "resume_extraction_failed"),
            (" \n\t ", "resume_text_empty"),
        ):
            with self.subTest(expected=expected):
                def download(_file_id, destination):
                    with open(destination, "wb") as file:
                        file.write(b"%PDF-")
                    return ".pdf"

                with patch("freelancer.utils.download_from_google_drive", side_effect=download), \
                        patch("freelancer.utils.read_file", side_effect=extracted), \
                        patch("freelancer.utils._analyze_text") as analyze:
                    with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                        resume_utils.analyze_resume(
                            "https://drive.google.com/file/d/file-id/view", 17
                        )
                self.assertEqual(raised.exception.code, expected)
                analyze.assert_not_called()

    def test_model_repair_retry_only_for_invalid_received_schema(self):
        valid = json.dumps(valid_resume_analysis(), ensure_ascii=False)
        for responses, expected_calls, error_code in (
            ([valid], 1, None),
            (["invalid JSON", valid], 2, None),
            (["invalid JSON", "{}"], 2, "analysis_invalid_response"),
        ):
            with self.subTest(expected_calls=expected_calls, error_code=error_code):
                client = Mock()
                client.chat.completions.create.side_effect = [
                    SimpleNamespace(
                        choices=[SimpleNamespace(
                            message=SimpleNamespace(content=text)
                        )]
                    )
                    for text in responses
                ]
                with patch("freelancer.utils.OpenAI", return_value=client) as factory, \
                        patch.dict(os.environ, {
                            "API_KEY": "test-key",
                            "OPEN_AI_BASE_URL": "https://provider.invalid",
                            "AI_MODEL": "test-model",
                        }):
                    if error_code:
                        with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                            resume_utils._analyze_text("test resume")
                        self.assertEqual(raised.exception.code, error_code)
                    else:
                        self.assertEqual(
                            resume_utils._analyze_text("test resume"),
                            valid_resume_analysis(),
                        )
                self.assertEqual(client.chat.completions.create.call_count, expected_calls)
                factory.assert_called_once()
                self.assertEqual(factory.call_args.kwargs["timeout"], 30.0)
                self.assertEqual(factory.call_args.kwargs["max_retries"], 0)
                self.assertEqual(
                    client.chat.completions.create.call_args_list[0].kwargs["timeout"],
                    30.0,
                )

    def test_provider_timeout_and_service_failures_are_not_retried(self):
        from openai import APITimeoutError, OpenAIError

        for exception, expected in (
            (APITimeoutError(request=Mock()), "analysis_provider_timeout"),
            (OpenAIError("private provider detail"), "analysis_unavailable"),
        ):
            with self.subTest(expected=expected):
                client = Mock()
                client.chat.completions.create.side_effect = exception
                with patch("freelancer.utils.OpenAI", return_value=client), \
                        patch.dict(os.environ, {
                            "API_KEY": "test-key",
                            "OPEN_AI_BASE_URL": "https://provider.invalid",
                            "AI_MODEL": "test-model",
                        }):
                    with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                        resume_utils._analyze_text("test resume")
                self.assertEqual(raised.exception.code, expected)
                client.chat.completions.create.assert_called_once()

    def test_provider_failure_during_repair_does_not_trigger_a_third_call(self):
        from openai import APITimeoutError

        client = Mock()
        client.chat.completions.create.side_effect = [
            SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(content="invalid"))
            ]),
            APITimeoutError(request=Mock()),
        ]
        with patch("freelancer.utils.OpenAI", return_value=client), \
                patch.dict(os.environ, {
                    "API_KEY": "test-key",
                    "OPEN_AI_BASE_URL": "https://provider.invalid",
                    "AI_MODEL": "test-model",
                }):
            with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                resume_utils._analyze_text("test resume")
        self.assertEqual(raised.exception.code, "analysis_provider_timeout")
        self.assertEqual(client.chat.completions.create.call_count, 2)

    def test_missing_provider_configuration_does_not_create_client(self):
        with patch("freelancer.utils.OpenAI") as factory, \
                patch.dict(os.environ, {
                    "API_KEY": "",
                    "OPEN_AI_BASE_URL": "",
                    "AI_MODEL": "",
                }):
            with self.assertRaises(resume_utils.ResumeAnalysisError) as raised:
                resume_utils._analyze_text("test resume")
        self.assertEqual(raised.exception.code, "analysis_unavailable")
        factory.assert_not_called()


class ResumeAnalysisViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        role = Role.objects.create(id=2)
        self.user = User.objects.create_user(
            email="resume-owner@example.com",
            password="test123",
            role=role,
            name="Resume",
            surname="Owner",
            phone="1234567890",
        )
        self.other_user = User.objects.create_user(
            email="other-owner@example.com",
            password="test123",
            role=role,
            name="Other",
            surname="Owner",
            phone="1234567891",
        )
        self.status = FreelancerStatus.objects.create(status="active")
        self.freelancer = Freelancer.objects.create(
            id_user=self.user,
            cv="https://drive.google.com/file/d/owned-id/view",
            experience=2,
            id_status=self.status,
        )
        self.other_freelancer = Freelancer.objects.create(
            id_user=self.other_user,
            cv="https://drive.google.com/file/d/other-id/view",
            experience=3,
            id_status=self.status,
        )
        self.url = reverse("freelancers:analyze_resume")

    def test_unauthenticated_get_redirects_and_post_returns_exact_401(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 302)
        self.assertTrue(get_response["Location"].startswith("/users/login/"))
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            "error": {
                "code": "authentication_required",
                "message": "Увійдіть, щоб аналізувати резюме.",
            },
        })
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"]["code"], "method_not_allowed")

    def test_owner_success_and_foreign_profile_selector_cannot_change_source(self):
        self.client.force_login(self.user)
        analysis = valid_resume_analysis()
        with patch("freelancer.views.analyze_resume", return_value=analysis) as analyze:
            response = self.client.post(self.url, {"freelancer_id": self.other_freelancer.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"analysis": analysis})
        analyze.assert_called_once_with(self.freelancer.cv, self.freelancer.id)

    def test_no_profile_get_and_post_have_controlled_behavior(self):
        self.client.force_login(User.objects.create_user(
            email="without-profile@example.com",
            password="test123",
            role=self.user.role,
            name="No",
            surname="Profile",
            phone="1234567892",
        ))
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Профіль фрілансера не знайдено.")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            "error": {
                "code": "freelancer_profile_not_found",
                "message": "Профіль фрілансера не знайдено.",
            },
        })

    def test_missing_cv_and_unsupported_method_have_exact_errors(self):
        self.client.force_login(self.user)
        self.freelancer.cv = ""
        self.freelancer.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            "error": {
                "code": "resume_reference_missing",
                "message": "Додайте посилання на резюме у своєму профілі.",
            },
        })
        self.freelancer.cv = " \n\t "
        self.freelancer.save()
        get_response = self.client.get(self.url)
        self.assertContains(get_response, "Ви ще не додали посилання на своє резюме.")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "resume_reference_missing")
        self.freelancer.cv = ""
        self.freelancer.save()
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {
            "error": {
                "code": "method_not_allowed",
                "message": "Ця дія не підтримується.",
            },
        })

    def test_service_errors_are_safe_and_preserve_specified_status(self):
        self.client.force_login(self.user)
        failures = (
            ("resume_retrieval_failed", 502,
             "Не вдалося отримати резюме з Google Drive. Перевірте доступ до посилання та спробуйте ще раз."),
            ("resume_file_invalid", 422,
             "Файл резюме не вдалося перевірити. Завантажте коректний файл PDF або DOCX."),
            ("resume_extraction_failed", 422,
             "Не вдалося прочитати текст резюме. Перевірте файл PDF або DOCX і спробуйте ще раз."),
            ("resume_text_empty", 422,
             "У резюме не знайдено тексту для аналізу. Перевірте файл і спробуйте ще раз."),
            ("analysis_invalid_response", 502,
             "Не вдалося сформувати коректний аналіз. Спробуйте ще раз пізніше."),
            ("analysis_provider_timeout", 504,
             "Сервіс аналізу не відповідає. Спробуйте ще раз пізніше."),
            ("analysis_unavailable", 503,
             "Аналіз резюме тимчасово недоступний. Спробуйте ще раз пізніше."),
            ("analysis_failed", 500,
             "Не вдалося виконати аналіз. Спробуйте ще раз пізніше."),
        )
        for code, status, message in failures:
            with self.subTest(code=code):
                with patch(
                    "freelancer.views.analyze_resume",
                    side_effect=resume_utils.ResumeAnalysisError(code),
                ):
                    response = self.client.post(self.url)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json(), {
                    "error": {"code": code, "message": message},
                })

    def test_unexpected_exception_details_are_not_returned(self):
        self.client.force_login(self.user)
        with patch(
            "freelancer.views.analyze_resume",
            side_effect=RuntimeError("private CV and provider data"),
        ):
            response = self.client.post(self.url)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            "error": {
                "code": "analysis_failed",
                "message": "Не вдалося виконати аналіз. Спробуйте ще раз пізніше.",
            },
        })
        self.assertNotIn("private CV and provider data", response.content.decode())

    def test_html_like_model_text_is_returned_as_data_and_template_uses_text(self):
        self.client.force_login(self.user)
        analysis = valid_resume_analysis()
        hostile_text = "<img src=x onerror=alert(1)> **not markup**"
        analysis["summary"] = hostile_text
        with patch("freelancer.views.analyze_resume", return_value=analysis):
            response = self.client.post(self.url)
        self.assertEqual(response.json(), {"analysis": analysis})
        page = self.client.get(self.url)
        self.assertNotContains(page, "innerHTML")
        self.assertContains(page, "textContent")
        self.assertContains(page, "replaceChildren")

    def test_each_trigger_runs_fresh_analysis_without_persisting_results(self):
        self.client.force_login(self.user)
        count_before = Freelancer.objects.count()
        with patch(
            "freelancer.views.analyze_resume",
            return_value=valid_resume_analysis(),
        ) as analyze:
            first = self.client.post(self.url)
            second = self.client.post(self.url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(analyze.call_count, 2)
        self.assertEqual(Freelancer.objects.count(), count_before)
        self.freelancer.refresh_from_db()
        self.assertEqual(
            self.freelancer.cv,
            "https://drive.google.com/file/d/owned-id/view",
        )


@contextmanager
def tempfile_test_path():
    with tempfile.TemporaryDirectory() as directory:
        yield os.path.join(directory, "resume")
