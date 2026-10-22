from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, transaction
from django.test.utils import CaptureQueriesContext
from django.test import TestCase, override_settings
from django.urls import reverse

from freelancer.models import Freelancer, FreelancerStatus
from notification.models import Notification
from project.models import Project, Status
from users.models import Role

from .models import WorkRequest, WorkRequestStatus
from .views import (
    INITIAL_STATUS,
    LIFECYCLE_STATUS_LABELS,
    _get_lifecycle_statuses,
    _get_status_by_label,
    apply_work_request_status_transition,
)


User = get_user_model()


class WorkRequestTestData:
    def setUp(self):
        self.owner = self.create_user("owner")
        self.other_owner = self.create_user("other-owner")
        self.freelancer_user = self.create_user("freelancer")
        self.freelancer = self.create_freelancer(self.freelancer_user)
        self.project_status = Status.objects.create(status="Відкрито")
        self.project = self.create_project(self.owner)
        self.assertEqual(
            WorkRequestStatus.objects.filter(status="На розгляді").count(), 1
        )
        self.statuses = {}
        for label in LIFECYCLE_STATUS_LABELS:
            if label == "На розгляді":
                self.statuses[label] = WorkRequestStatus.objects.get(status=label)
            else:
                self.statuses[label] = WorkRequestStatus.objects.get_or_create(
                    status=label
                )[0]
        self.client.force_login(self.owner)

    def create_user(self, name):
        role, _ = Role.objects.get_or_create(role="Lifecycle test")
        return User.objects.create_user(
            email=f"{name}@example.com",
            password="test-password",
            name=name,
            surname="Tester",
            phone=f"{name[:14]}-phone",
            role=role,
        )

    def create_freelancer(self, user):
        status, _ = FreelancerStatus.objects.get_or_create(status="Available")
        return Freelancer.objects.create(id_user=user, id_status=status)

    def create_project(self, owner):
        return Project.objects.create(
            user=owner,
            status=self.project_status,
            name="Lifecycle project",
            description="Project for lifecycle tests",
        )

    def create_request(self, freelancer=None, status_label=INITIAL_STATUS, project=None):
        freelancer = freelancer or self.freelancer
        return WorkRequest.objects.create(
            id_status=self.statuses[status_label],
            id_freelancer=freelancer,
            id_project=project or self.project,
            created_at="2026-10-20",
        )

    def post_status(self, work_request, status_label, client=None):
        client = client or self.client
        return client.post(
            reverse(
                "workrequest:change_request_status",
                args=[work_request.id_project_id, work_request.id_freelancer_id],
            ),
            {"status_id": self.statuses[status_label].id},
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class WorkRequestLifecycleTests(WorkRequestTestData, TestCase):
    def test_initial_status_is_selected_by_label_not_row_order(self):
        self.assertNotEqual(WorkRequestStatus.objects.first().status, INITIAL_STATUS)
        self.client.force_login(self.freelancer_user)

        self.client.get(
            reverse("workrequest:create_work_request", args=[self.project.id])
        )

        created = WorkRequest.objects.get(
            id_project=self.project, id_freelancer=self.freelancer
        )
        self.assertEqual(created.id_status.status, INITIAL_STATUS)
        self.assertEqual(
            Notification.objects.filter(id_receiver=self.owner).count(), 1
        )
        self.assertIn(
            "sent a collaboration request",
            Notification.objects.get(id_receiver=self.owner).message,
        )

    def test_missing_or_ambiguous_required_status_fails_explicitly(self):
        for label in LIFECYCLE_STATUS_LABELS:
            WorkRequestStatus.objects.filter(status=label).delete()
            with self.assertRaises(ImproperlyConfigured):
                _get_status_by_label(label)
            with self.assertRaises(ImproperlyConfigured):
                _get_lifecycle_statuses()
            WorkRequestStatus.objects.create(status=label)
            WorkRequestStatus.objects.create(status=label)
            with self.assertRaises(ImproperlyConfigured):
                _get_status_by_label(label)
            with self.assertRaises(ImproperlyConfigured):
                _get_lifecycle_statuses()
            WorkRequestStatus.objects.filter(status=label).delete()
            WorkRequestStatus.objects.create(status=label)

    def test_migration_provides_exactly_one_reviewing_status(self):
        self.assertEqual(
            WorkRequestStatus.objects.filter(status="На розгляді").count(), 1
        )

    def test_each_approved_transition_succeeds(self):
        request = self.create_request()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.post_status(request, "На розгляді")
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, "На розгляді")

        with self.captureOnCommitCallbacks(execute=True):
            response = self.post_status(request, "Схвалено")
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, "Схвалено")

        rejected_request = self.create_request(
            freelancer=self.create_freelancer(self.create_user("second-freelancer"))
        )
        with self.captureOnCommitCallbacks(execute=True):
            self.post_status(rejected_request, "На розгляді")
            response = self.post_status(rejected_request, "Відхилено")
        self.assertEqual(response.status_code, 302)
        rejected_request.refresh_from_db()
        self.assertEqual(rejected_request.id_status.status, "Відхилено")

        direct_approval = self.create_request(
            freelancer=self.create_freelancer(self.create_user("direct-approval"))
        )
        direct_rejection = self.create_request(
            freelancer=self.create_freelancer(self.create_user("direct-rejection"))
        )
        with self.captureOnCommitCallbacks(execute=True):
            approved_response = self.post_status(direct_approval, "Схвалено")
            rejected_response = self.post_status(direct_rejection, "Відхилено")
        self.assertEqual(approved_response.status_code, 302)
        self.assertEqual(rejected_response.status_code, 302)
        direct_approval.refresh_from_db()
        direct_rejection.refresh_from_db()
        self.assertEqual(direct_approval.id_status.status, "Схвалено")
        self.assertEqual(direct_rejection.id_status.status, "Відхилено")

    def test_terminal_transitions_do_not_mutate(self):
        for terminal in ("Схвалено", "Відхилено"):
            request = self.create_request(
                freelancer=self.create_freelancer(self.create_user(f"terminal-{terminal}")),
                status_label=terminal,
            )
            for label in LIFECYCLE_STATUS_LABELS:
                if label == terminal:
                    continue
                response = self.post_status(request, label)
                self.assertEqual(response.status_code, 400)
                request.refresh_from_db()
                self.assertEqual(request.id_status.status, terminal)

    def test_non_lifecycle_status_is_rejected_without_mutation(self):
        request = self.create_request()
        unknown_status = WorkRequestStatus.objects.create(status="Невідомий")
        response = self.client.post(
            reverse(
                "workrequest:change_request_status",
                args=[request.id_project_id, request.id_freelancer_id],
            ),
            {"status_id": unknown_status.id},
        )
        self.assertEqual(response.status_code, 400)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, INITIAL_STATUS)

    def test_owner_authorization_and_unauthorized_denial(self):
        request = self.create_request()
        non_owner_client = self.client_class()
        non_owner_client.force_login(self.other_owner)
        response = self.post_status(request, "На розгляді", non_owner_client)
        self.assertEqual(response.status_code, 403)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, INITIAL_STATUS)

        anonymous_client = self.client_class()
        response = self.post_status(request, "На розгляді", anonymous_client)
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, INITIAL_STATUS)

    def test_only_selected_request_changes_and_project_status_is_unchanged(self):
        approved_competitor = self.create_request(
            freelancer=self.create_freelancer(
                self.create_user("approved-competitor")
            ),
            status_label="Схвалено",
        )
        rejected_competitor = self.create_request(
            freelancer=self.create_freelancer(
                self.create_user("rejected-competitor")
            ),
            status_label="Відхилено",
        )
        selected = self.create_request(
            freelancer=self.create_freelancer(self.create_user("selected"))
        )
        rejected_selected = self.create_request(
            freelancer=self.create_freelancer(
                self.create_user("rejected-selected")
            )
        )
        initial_project_status_id = self.project.status_id

        with self.captureOnCommitCallbacks(execute=True):
            self.post_status(selected, "На розгляді")
            self.post_status(selected, "Схвалено")
            self.post_status(rejected_selected, "На розгляді")
            self.post_status(rejected_selected, "Відхилено")

        selected.refresh_from_db()
        rejected_selected.refresh_from_db()
        approved_competitor.refresh_from_db()
        rejected_competitor.refresh_from_db()
        self.project.refresh_from_db()
        self.assertEqual(selected.id_status.status, "Схвалено")
        self.assertEqual(rejected_selected.id_status.status, "Відхилено")
        self.assertEqual(approved_competitor.id_status.status, "Схвалено")
        self.assertEqual(rejected_competitor.id_status.status, "Відхилено")
        self.assertEqual(self.project.status_id, initial_project_status_id)

    def test_status_change_notification_occurs_once_only_for_real_transition(self):
        request = self.create_request()
        with self.captureOnCommitCallbacks(execute=True):
            self.post_status(request, "На розгляді")
        notifications = Notification.objects.filter(
            id_receiver=self.freelancer_user,
            message__contains="New status:",
        )
        self.assertEqual(notifications.count(), 1)
        self.assertIn("На розгляді", notifications.get().message)

        request.refresh_from_db()
        request.save()
        self.assertEqual(notifications.count(), 1)

        with self.captureOnCommitCallbacks(execute=True):
            self.post_status(request, "Схвалено")
        self.assertEqual(notifications.count(), 2)

        with self.captureOnCommitCallbacks(execute=True):
            self.post_status(request, "Схвалено")
        self.assertEqual(notifications.count(), 2)

    def test_rolled_back_transition_does_not_notify(self):
        request = self.create_request()
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError):
                with transaction.atomic():
                    apply_work_request_status_transition(
                        user=self.owner,
                        target_status_id=self.statuses["На розгляді"].id,
                        work_request_id=request.id,
                    )
                    raise RuntimeError("rollback")

        request.refresh_from_db()
        self.assertEqual(request.id_status.status, INITIAL_STATUS)
        self.assertFalse(
            Notification.objects.filter(id_receiver=self.freelancer_user).exists()
        )

    def test_transition_query_locks_the_selected_request_where_supported(self):
        if not connection.features.has_select_for_update:
            self.skipTest("Database backend does not support SELECT FOR UPDATE.")
        request = self.create_request()
        with self.captureOnCommitCallbacks(execute=False):
            with CaptureQueriesContext(connection) as queries:
                apply_work_request_status_transition(
                    user=self.owner,
                    target_status_id=self.statuses["На розгляді"].id,
                    work_request_id=request.id,
                )
        self.assertTrue(
            any("FOR UPDATE" in query["sql"].upper() for query in queries.captured_queries)
        )
        self.assertEqual(request.id_status.status, INITIAL_STATUS)

    def test_owner_and_freelancer_status_filters_remain_available(self):
        accepted = self.create_request(status_label="Схвалено")
        self.create_request(
            freelancer=self.create_freelancer(self.create_user("filtered-out")),
            status_label="Відхилено",
        )

        employer_response = self.client.get(
            reverse("workrequest:employer_request"),
            {"status": self.statuses["Схвалено"].id},
        )
        self.assertEqual(employer_response.status_code, 200)
        self.assertEqual(list(employer_response.context["work_request"]), [accepted])

        freelancer_client = self.client_class()
        freelancer_client.force_login(self.freelancer_user)
        freelancer_response = freelancer_client.get(
            reverse("workrequest:freelancer_request"),
            {"status": self.statuses["Схвалено"].id},
        )
        self.assertEqual(freelancer_response.status_code, 200)
        self.assertEqual(list(freelancer_response.context["work_request"]), [accepted])

    def test_duplicate_work_request_protection_remains(self):
        self.client.force_login(self.freelancer_user)
        self.client.get(
            reverse("workrequest:create_work_request", args=[self.project.id])
        )
        self.client.get(
            reverse("workrequest:create_work_request", args=[self.project.id])
        )
        self.assertEqual(
            WorkRequest.objects.filter(
                id_project=self.project, id_freelancer=self.freelancer
            ).count(),
            1,
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminWorkRequestLifecycleTests(WorkRequestTestData, TestCase):
    def test_admin_mutation_uses_same_lifecycle_and_owner_authorization(self):
        request = self.create_request()
        url = reverse("adminp:update_work_request_a", args=[request.id])
        response = self.client.post(
            url,
            {
                "status": self.statuses["Схвалено"].id,
                "project": self.project.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, "Схвалено")

        reviewed_request = self.create_request(
            freelancer=self.create_freelancer(self.create_user("admin-review-flow"))
        )
        url = reverse("adminp:update_work_request_a", args=[reviewed_request.id])
        response = self.client.post(
            url,
            {
                "status": self.statuses["На розгляді"].id,
                "project": self.project.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        reviewed_request.refresh_from_db()
        self.assertEqual(reviewed_request.id_status.status, "На розгляді")

        response = self.client.post(
            url,
            {
                "status": self.statuses["Схвалено"].id,
                "project": self.project.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        reviewed_request.refresh_from_db()
        self.assertEqual(reviewed_request.id_status.status, "Схвалено")

    def test_admin_route_rejects_non_owner_project_change_and_anonymous_user(self):
        request = self.create_request()
        another_project = self.create_project(self.other_owner)
        url = reverse("adminp:update_work_request_a", args=[request.id])

        response = self.client.post(
            url,
            {
                "status": self.statuses["На розгляді"].id,
                "project": another_project.id,
            },
        )
        self.assertEqual(response.status_code, 400)
        request.refresh_from_db()
        self.assertEqual(request.id_project_id, self.project.id)
        self.assertEqual(request.id_status.status, INITIAL_STATUS)

        non_owner_client = self.client_class()
        non_owner_client.force_login(self.other_owner)
        response = non_owner_client.post(
            url,
            {
                "status": self.statuses["На розгляді"].id,
                "project": self.project.id,
            },
        )
        self.assertEqual(response.status_code, 403)

        anonymous_client = self.client_class()
        response = anonymous_client.post(
            url,
            {
                "status": self.statuses["На розгляді"].id,
                "project": self.project.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.id_status.status, INITIAL_STATUS)
