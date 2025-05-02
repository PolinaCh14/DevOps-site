from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import WorkRequest, WorkRequestStatus
from django.contrib.auth.decorators import login_required
from users.models import User
from project.models import Project
from freelancer.models import Freelancer
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponseNotFound, HttpResponseBadRequest

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
@login_required
def change_request_status(request, project_id, freelancer_id):
    if request.method == 'POST':
        status_id = request.POST.get('status_id')
        if status_id is not None:
            try:
                status_id = int(status_id)
            except ValueError:
                return HttpResponseBadRequest("Невірний формат статусу.")
        else:
            return HttpResponseBadRequest("Статус не був переданий.")

        project = get_object_or_404(Project, id=project_id)

        if status_id == 2:
            work_requests = WorkRequest.objects.filter(id_project=project_id)
            for i in work_requests:
                if i.id_freelancer.id == freelancer_id:
                    i.id_status_id = status_id
                    project.status.id = 2
                else:
                    i.id_status_id = 3
                i.save()
            project.save()
        else:
            try:
                work_request = WorkRequest.objects.get(id_project=project_id, id_freelancer=freelancer_id)
                work_request.id_status_id = status_id
                work_request.save()
            except WorkRequest.DoesNotExist:
                return HttpResponseBadRequest("Запит не знайдено.")

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
    user = request.user

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

    default_status = WorkRequestStatus.objects.first()
    if not default_status:
        messages.error(request, "Немає статусів для запиту. Зверніться до адміністратора.")
        return redirect('projects:project', project_id=project_id)

    WorkRequest.objects.create(
        id_status=default_status,
        id_freelancer_id=freelancer.id,
        id_project_id=project_id,
        created_at=now().date()
    )

    messages.success(request, "Заявку успішно подано.")
    return redirect('projects:projects_search_view')

