from django.shortcuts import render, redirect, get_object_or_404
from .models import WorkRequest, WorkRequestStatus
from django.contrib.auth.decorators import login_required
from project.models import Project
from freelancer.models import Freelancer
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponseBadRequest
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.db import transaction
from django.views.decorators.http import require_http_methods
from notification.signals import notify_freelancer_on_status_change


INITIAL_STATUS = "В очікуванні"
LIFECYCLE_STATUS_LABELS = (
    INITIAL_STATUS,
    "На розгляді",
    "Схвалено",
    "Відхилено",
)
ALLOWED_TRANSITIONS = {
    INITIAL_STATUS: {"На розгляді", "Схвалено", "Відхилено"},
    "На розгляді": {"Схвалено", "Відхилено"},
    "Схвалено": set(),
    "Відхилено": set(),
}


def _get_status_by_label(label):
    try:
        return WorkRequestStatus.objects.get(status=label)
    except (WorkRequestStatus.DoesNotExist, WorkRequestStatus.MultipleObjectsReturned) as exc:
        raise ImproperlyConfigured(
            f"Expected exactly one WorkRequestStatus labeled {label!r}."
        ) from exc


def _get_lifecycle_statuses():
    return {label: _get_status_by_label(label) for label in LIFECYCLE_STATUS_LABELS}


def apply_work_request_status_transition(
    *,
    user,
    target_status_id,
    work_request_id=None,
    project_id=None,
    freelancer_id=None,
    submitted_project_id=None,
):
    with transaction.atomic():
        work_requests = WorkRequest.objects.select_for_update()
        if work_request_id is not None:
            work_request = get_object_or_404(work_requests, id=work_request_id)
        else:
            work_request = get_object_or_404(
                work_requests,
                id_project_id=project_id,
                id_freelancer_id=freelancer_id,
            )

        if not work_request.id_project_id or not work_request.id_freelancer_id:
            raise ValidationError("Work request must have a project and freelancer.")
        if submitted_project_id is not None and work_request.id_project_id != submitted_project_id:
            raise ValidationError("Changing a work request's project is not permitted.")
        if work_request.id_project.user_id != user.id:
            raise PermissionDenied

        statuses = _get_lifecycle_statuses()
        try:
            target_status = WorkRequestStatus.objects.get(id=target_status_id)
        except WorkRequestStatus.DoesNotExist as exc:
            raise ValidationError("Unknown work request status.") from exc

        if target_status.status not in statuses:
            raise ValidationError("Status is not part of the approved lifecycle.")

        current_label = work_request.id_status.status
        target_label = target_status.status
        if current_label == target_label:
            return work_request
        if target_label not in ALLOWED_TRANSITIONS.get(current_label, set()):
            raise ValidationError(
                f"Transition from {current_label!r} to {target_label!r} is not permitted."
            )

        work_request.id_status = statuses[target_label]
        work_request.save(update_fields=["id_status"])
        transaction.on_commit(
            lambda: notify_freelancer_on_status_change(work_request)
        )

    return work_request

@login_required
def freelancer_work_request(request):
    freelancer = Freelancer.objects.get(id_user=request.user.id)

    status_id = request.GET.get('status')

    if status_id:
        work_request = WorkRequest.objects.filter(id_freelancer=freelancer.id, id_status_id=status_id)
    else:
        work_request = WorkRequest.objects.filter(id_freelancer=freelancer.id)

    statuses = WorkRequestStatus.objects.all()

    return render(
        request,
        'freelancer-work-request.html',
        {
            'work_request': work_request,
            'statuses': statuses,
            'selected_status': int(status_id) if status_id else None
        }
    )


@login_required
def employer_work_request(request):
    projects = Project.objects.filter(user_id=request.user.id)

    status_id = request.GET.get('status')

    if status_id:
        work_request = WorkRequest.objects.filter(id_project__in=projects, id_status_id=status_id)
    else:
        work_request = WorkRequest.objects.filter(id_project__in=projects)

    statuses = WorkRequestStatus.objects.all()

    return render(
        request,
        'freelancer-work-request.html',
        {
            'work_request': work_request,
            'statuses': statuses,
            'selected_status': int(status_id) if status_id else None
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def change_request_status(request, project_id, freelancer_id):
    if request.method == 'POST':
        status_id = request.POST.get('status_id')
        if status_id is None:
            return HttpResponseBadRequest("Статус не був переданий.")
        try:
            status_id = int(status_id)
            apply_work_request_status_transition(
                user=request.user,
                target_status_id=status_id,
                project_id=project_id,
                freelancer_id=freelancer_id,
            )
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Невірний формат статусу.")
        except ValidationError as exc:
            return HttpResponseBadRequest(str(exc))

        return redirect('workrequest:employer_request')

    projects = Project.objects.filter(user_id=request.user.id)
    work_requests = WorkRequest.objects.filter(id_project__in=projects)
    statuses = WorkRequestStatus.objects.all()
    return render(request, 'update_request_status.html', {
        'work_requests': work_requests,
        'statuses': statuses
    })

@login_required
def create_work_request(request, project_id):
    freelancer = Freelancer.objects.get(id_user=request.user.id)
    if not freelancer:
        raise ValueError("Фрілансер з таким користувачем не знайдений")

    existing_request = WorkRequest.objects.filter(
        id_project_id=project_id,
        id_freelancer_id=freelancer.id
    ).first()

    if existing_request:
        messages.error(request, "Ви вже подали заявку на цей проєкт.")
        return redirect('projects:project', project_id=project_id)

    default_status = _get_status_by_label(INITIAL_STATUS)

    WorkRequest.objects.create(
        id_status=default_status,
        id_freelancer_id=freelancer.id,
        id_project_id=project_id,
        created_at=now().date()
    )

    messages.success(request, "Заявку успішно подано.")
    return redirect('projects:projects_search_view')
