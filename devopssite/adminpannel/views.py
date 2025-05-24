from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from freelancer.models import Freelancer, FreelancerStatus, FreelancerSkill, Portfolio
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from workrequest.models import WorkRequest, WorkRequestStatus
from users.models import User, Role
from rating.utils import get_average_rating_for_user
from project.models import Project, ProjectSkill, Status
from skill.models import Skill
from django.views.decorators.http import require_POST
# Create your views here.


@login_required
def get_all_user(request):
    role_filter = request.GET.get('role', '')
    surname_filter = request.GET.get('surname', '')

    roles = Role.objects.all()

    users = User.objects.all()

    if role_filter:
        users = users.filter(role__role=role_filter)

    if surname_filter:
        users = users.filter(surname__icontains=surname_filter)

    return render(request, 'all_users.html', {
        'users': users,
        'roles': roles,
        'selected_role': role_filter,
        'selected_surname': surname_filter,
    })

@login_required()
def user_profile(request, id):
    user = get_object_or_404(User, id=id)
    raw_rating = get_average_rating_for_user(user.id)
    rating = round(raw_rating) if raw_rating is not None else 0

    context = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "profile_picture": user.profile_picture,
        "role": user.role.role,
        "rating": rating,
    }

    return render(request, 'user.page.html', context)


@login_required
def update_user_profile(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        phone = request.POST.get('phone')
        about_me = request.POST.get('about_me')
        profile_picture = request.POST.get('profile_picture')
        email = request.POST.get('email')

        updated = False

        if name and name != user.name:
            user.name = name
            updated = True

        if surname and surname != user.surname:
            user.surname = surname
            updated = True

        if phone and phone != user.phone:
            user.phone = phone
            updated = True

        if about_me and about_me != user.about_me:
            user.about_me = about_me
            updated = True

        if profile_picture and profile_picture != user.profile_picture:
            user.profile_picture = profile_picture
            updated = True

        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'Користувач з такою електронною поштою вже існує.')
                return redirect('users:profile')
            user.email = email
            updated = True

        if updated:
            user.save()
            messages.success(request, 'Профіль успішно оновлено.')
        else:
            messages.info(request, 'Зміни не були внесені.')

        return redirect('adminp:user_profile_a', id=user.id)

    return render(request, 'update_profile.html', {'user': user})


@require_POST
@login_required
def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    messages.success(request, 'Користувача успішно видалено.')
    return redirect('adminp:all_users')

# project !!!!!!!!!

def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        status_id = request.POST.get('status')
        execution = request.POST.get('execution')
        end_at = request.POST.get('end_at')
        price = request.POST.get('price')
        skill_ids = request.POST.getlist('skills')

        updated = False

        if name and name != project.name:
            project.name = name
            updated = True

        if description and description != project.description:
            project.description = description
            updated = True

        if status_id and int(status_id) != project.status.id:
            project.status = Status.objects.get(id=status_id)
            updated = True

        if execution != '' and execution != str(project.execution):
            project.execution = int(execution)
            updated = True

        if end_at != '' and end_at != str(project.end_at):
            project.end_at = end_at
            updated = True

        if price != '' and price != str(project.price):
            project.price = price
            updated = True

        if updated:
            project.save()

        ProjectSkill.objects.filter(id_project=project).delete()
        for skill_id in skill_ids:
            skill = Skill.objects.get(id=skill_id)
            ProjectSkill.objects.create(id_project=project, id_skill=skill)

        return redirect('projects:user_project', project_id=project.id)

    statuses = Status.objects.all()
    skills = Skill.objects.all()
    current_skills = project.projectskill_set.values_list('id_skill_id', flat=True)

    return render(request, 'update_project.html', {
        'project': project,
        'statuses': statuses,
        'skills': skills,
        'current_skills': current_skills,
    })

def projects_search_view(request):
    projects = Project.objects.all()
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
    return render(request, 'all_users_projects.html', context)


# freelancer !!!!


def freelancer_list(request):
    freelancers = Freelancer.objects.select_related('id_user', 'id_status').all()
    statuses = FreelancerStatus.objects.all()
    skills = Skill.objects.all()

    name = request.GET.get('name')
    status_id = request.GET.get('status')
    skill_id = request.GET.get('skill')
    experience = request.GET.get('experience')
    experience_filter = request.GET.get('experience_filter')
    rating = request.GET.get('rating')
    rating_filter = request.GET.get('rating_filter')

    if name:
        freelancers = freelancers.filter(
            Q(id_user__name__icontains=name) |
            Q(id_user__surname__icontains=name)
        )

    if status_id:
        freelancers = freelancers.filter(id_status_id=status_id)

    if skill_id:
        freelancers = freelancers.filter(
            id__in=FreelancerSkill.objects.filter(
                id_skill_id=skill_id
            ).values_list('id_freelancer', flat=True)
        )

    if experience and experience_filter:
        try:
            experience = int(experience)
            experience_filters = {
                'lt': 'experience__lt',
                'lte': 'experience__lte',
                'eq': 'experience',
                'gte': 'experience__gte',
                'gt': 'experience__gt'
            }
            if experience_filter in experience_filters:
                freelancers = freelancers.filter(**{
                    experience_filters[experience_filter]: experience
                })
        except ValueError:
            pass

    rating = request.GET.get('rating')
    rating_filter = request.GET.get('rating_filter')

    if rating and rating_filter:
        try:
            rating = float(rating)
            ops = {
                'lt': lambda r: r < rating,
                'lte': lambda r: r <= rating,
                'eq': lambda r: r == rating,
                'gte': lambda r: r >= rating,
                'gt': lambda r: r > rating,
            }

            if rating_filter in ops:
                freelancers = [
                    f for f in freelancers
                    if (raw := get_average_rating_for_user(f.id_user.id)) is not None
                       and ops[rating_filter](raw)
                ]
        except ValueError:
            pass

    context = {
        'freelancers': freelancers,
        'statuses': statuses,
        'skills': skills,
        'request': request,
    }

    return render(request, 'freelancer_list_a.html', context)

def freelancer_detail(request, freelancer_id):
    freelancer = get_object_or_404(
        Freelancer.objects.select_related('id_user', 'id_status'),
        id=freelancer_id
    )
    raw_rating = get_average_rating_for_user(int(freelancer.id_user.id))
    rating = round(raw_rating) if raw_rating is not None else 0
    skills = FreelancerSkill.objects.select_related('id_skill').filter(id_freelancer=freelancer)
    portfolio = freelancer.portfolio_set.all()

    return render(request, 'freelancer_detail_a.html', {
        'freelancer': freelancer,
        'freelancer_user': freelancer.id_user,
        'skills': skills,
        'portfolio': portfolio,
        'rating': rating,
    })



@login_required
def update_freelancer_profile(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    statuses = FreelancerStatus.objects.all()
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        freelancer.cv = request.POST.get('cv', '')
        try:
            freelancer.experience = int(request.POST.get('experience', 0))
        except ValueError:
            pass

        status_id = request.POST.get('status')
        if status_id:
            try:
                freelancer.id_status_id = int(status_id)
            except ValueError:
                pass

        freelancer.save()

        selected_skill_ids = request.POST.getlist('skills')

        FreelancerSkill.objects.filter(id_freelancer=freelancer).delete()

        for skill_id in selected_skill_ids:
            try:
                skill_obj = Skill.objects.get(id=int(skill_id))
                FreelancerSkill.objects.create(id_freelancer=freelancer, id_skill=skill_obj)
            except (Skill.DoesNotExist, ValueError):
                continue

        return redirect('adminp:freelancer_detail_a', freelancer_id=freelancer.id)

    existing_skill_ids = FreelancerSkill.objects.filter(id_freelancer=freelancer).values_list('id_skill_id', flat=True)

    return render(request, 'freelancer_profile_edit.html', {
        'freelancer': freelancer,
        'statuses': statuses,
        'skills': all_skills,
        'existing_skill_ids': existing_skill_ids,
    })

@login_required
def create_portfolio_item(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        photo = request.POST.get('photo', '').strip()
        url = request.POST.get('url', '').strip()

        if title:
            Portfolio.objects.create(
                id_freelancer=freelancer,
                title=title,
                description=description,
                photo=photo,
                url=url
            )
            return redirect('adminp:freelancer_detail_a', freelancer_id=freelancer.id)

    return render(request, 'portfolio_create.html')


@login_required
def update_portfolio_item(request, item_id):
    portfolio_item = get_object_or_404(Portfolio, id=item_id)

    if request.method == 'POST':
        portfolio_item.title = request.POST.get('title', '').strip()
        portfolio_item.description = request.POST.get('description', '').strip()
        portfolio_item.photo = request.POST.get('photo', '').strip()
        portfolio_item.url = request.POST.get('url', '').strip()
        portfolio_item.save()

        return redirect('adminp:get_user_portfolio_a', portfolio_id=portfolio_item.id)

    return render(request, 'portfolio_update.html', {
        'item': portfolio_item
    })

@login_required
def delete_portfolio_item(request, item_id):
    portfolio_item = get_object_or_404(Portfolio, id=item_id)

    if request.method == 'POST':
        portfolio_item.delete()
        return redirect('adminp:freelancer_list_a')

    return render(request, 'portfolio_confirm_delete.html', {
        'item': portfolio_item
    })


def get_user_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    freelancer = get_object_or_404(Freelancer, id=portfolio.id_freelancer.id)
    return render(request, 'user_portfolio_a.html', {'portfolio': portfolio, 'freelancer': freelancer})


@login_required
def all_work_request(request):

    work_requests = WorkRequest.objects.all()

    statuses = WorkRequestStatus.objects.all()

    return render(
        request,
        'all_work_request.html',
        {
            'work_requests': work_requests,
            'statuses': statuses,
        }
    )
