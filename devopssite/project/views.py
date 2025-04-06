from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Project, ProjectSkill, Status
from skill.models import Skill
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def all_project_view(request):
    projects = Project.objects.all()
    return render(request, 'all_projects.html', {'projects': projects})

def all_open_project_view(request):
    projects = Project.objects.filter(status__name='Відкритий')
    return render(request, 'all_projects.html', {'projects': projects})

@login_required
def users_projects_view(request):
    projects = Project.objects.filter(user_id=request.user.id)
    return render(request, 'all_projects.html', {'projects': projects})

def users_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    skills = ProjectSkill.objects.filter(id_project=project).select_related('id_skill')
    return render(request, 'user_project.html', {'project': project, 'skills': skills})
def project_by_name(request, name):
    project = Project.objects.filter(name=name, status__name='Відкритий')
    return render(request, 'project.html', {'project': project})

def project_by_status(request, status):
    project = Project.objects.filter(status__id=status)
    return render(request, 'project.html', {'project': project})

def projects_by_skill(request, skill_name):
    projects = Project.objects.filter(skills__name=skill_name)
    return render(request, 'project_by_skill.html', {'projects': projects})

@login_required
def user_projects_search_view(request):
    projects = Project.objects.filter(user_id=request.user.id)
    statuses = Status.objects.all()
    skills = Skill.objects.all()

    name = request.GET.get('name')
    skill_id = request.GET.get('skill')
    status_id = request.GET.get('status')
    price = request.GET.get('price')
    price_filter = request.GET.get('price_filter')

    if name:
        projects = projects.filter(name__icontains=name)

    if status_id:
        projects = projects.filter(status_id=status_id)

    if skill_id:
        projects = projects.filter(
            id__in=ProjectSkill.objects.filter(
                id_skill_id=skill_id
            ).values_list('id_project', flat=True)
        )

    if price and price_filter:
        try:
            price = float(price)
            price_filters = {
                'lt': 'price__lt',
                'lte': 'price__lte',
                'eq': 'price',
                'gte': 'price__gte',
                'gt': 'price__gt'
            }
            if price_filter in price_filters:
                projects = projects.filter(**{price_filters[price_filter]: price})
        except ValueError:
            pass

    context = {
        'projects': projects,
        'statuses': statuses,
        'skills': skills,
        'request': request,  # для шаблону, якщо не включено в context_processors
    }
    return render(request, 'all_users_projects.html', context)


def projects_search_view(request):
    projects = Project.objects.filter(status__status='Відкрито')
    statuses = Status.objects.all()
    skills = Skill.objects.all()

    name = request.GET.get('name')
    skill_id = request.GET.get('skill')
    status_id = request.GET.get('status')
    price = request.GET.get('price')
    price_filter = request.GET.get('price_filter')

    if name:
        projects = projects.filter(name__icontains=name)

    if status_id:
        projects = projects.filter(status_id=status_id)

    if skill_id:
        projects = projects.filter(
            id__in=ProjectSkill.objects.filter(
                id_skill_id=skill_id
            ).values_list('id_project', flat=True)
        )

    if price and price_filter:
        try:
            price = float(price)
            price_filters = {
                'lt': 'price__lt',
                'lte': 'price__lte',
                'eq': 'price',
                'gte': 'price__gte',
                'gt': 'price__gt'
            }
            if price_filter in price_filters:
                projects = projects.filter(**{price_filters[price_filter]: price})
        except ValueError:
            pass

    context = {
        'projects': projects,
        'statuses': statuses,
        'skills': skills,
        'request': request,
    }
    return render(request, 'all_projects.html', context)

def project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    skills = ProjectSkill.objects.filter(id_project=project).select_related('id_skill')
    return render(request, 'project.html', {'project': project, 'skills': skills})