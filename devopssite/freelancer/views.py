from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Freelancer, FreelancerStatus, FreelancerSkill, Portfolio
from skill.models import Skill
from users.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def get_all_portfolio(request, freelancer_id):
    portfolio = Portfolio.objects.filter(id_freelancer = freelancer_id)
    return render()

def get_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    return render(request, 'portfolio.html', {'portfolio': portfolio})

@login_required
def create_portfolio(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        photo = request.POST.get('photo')
        description = request.POST.get('description')
        url = request.POST.get('url')

        portfolio = Portfolio.objects.create(
            id_freelancer=request.user,
            title=title,
            photo=photo,
            description=description,
            url=url if url else "",
        )

        return redirect('freelancers:portfolio', portfolio_id=portfolio.id)

    return render(request, 'create_portfolio.html')

def portfolio_delete(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    portfolio.delete()
    return redirect('freelancers:')

def update_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        photo = request.POST.get('photo')
        description = request.POST.get('description')
        url = request.POST.get('url') # нові скіли

        updated = False

        if title != '' and title != str(portfolio.title):
            portfolio.title = title
            updated = True

        if photo != '' and photo != str(portfolio.photo):
            portfolio.photo = photo
            updated = True


        if description != '' and description != str(portfolio.description):
            portfolio.description = int(description)
            updated = True

        if url != '' and url != str(portfolio.url):
            portfolio.end_at = url
            updated = True

        if updated:
            portfolio.save()

        return redirect('freelancer:user_portfolio', portfolio_id=portfolio.id)

    return render(request, 'update_portfolio.html', {
        'portfolio': portfolio
    })


# def freelancer_list(request):
#     freelancers = Freelancer.objects.select_related('id_user', 'id_status').all()
#
#     min_experience = request.GET.get('min_experience')
#     max_experience = request.GET.get('max_experience')
#
#     if min_experience:
#         freelancers = freelancers.filter(experience__gte=int(min_experience))
#     if max_experience:
#         freelancers = freelancers.filter(experience__lte=int(max_experience))
#
#     skill_ids = request.GET.getlist('skills')
#     if skill_ids:
#         freelancers = freelancers.filter(
#             freelancerskill__id_skill__in=skill_ids
#         ).distinct()
#
#     skills = Skill.objects.all()
#
#     context = {
#         'freelancers': freelancers,
#         'skills': skills,
#     }
#     return render(request, 'freelancer_list.html', context)


def freelancer_list(request):
    freelancers = Freelancer.objects.select_related('id_user', 'id_status').all()
    statuses = FreelancerStatus.objects.all()
    skills = Skill.objects.all()

    # Параметри з GET-запиту
    name = request.GET.get('name')
    status_id = request.GET.get('status')
    skill_id = request.GET.get('skill')
    experience = request.GET.get('experience')
    experience_filter = request.GET.get('experience_filter')

    # 🔎 Пошук по імені та прізвищу (user.name + user.surname)
    if name:
        freelancers = freelancers.filter(
            Q(id_user__name__icontains=name) |
            Q(id_user__surname__icontains=name)
        )

    # 🔎 Фільтр за статусом
    if status_id:
        freelancers = freelancers.filter(id_status_id=status_id)

    # 🔎 Фільтр за скілом
    if skill_id:
        freelancers = freelancers.filter(
            id__in=FreelancerSkill.objects.filter(
                id_skill_id=skill_id
            ).values_list('id_freelancer', flat=True)
        )

    # 🔎 Фільтр за досвідом
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

    context = {
        'freelancers': freelancers,
        'statuses': statuses,
        'skills': skills,
        'request': request,
    }

    return render(request, 'freelancer_list.html', context)


def freelancer_detail(request, freelancer_id):
    freelancer = get_object_or_404(
        Freelancer.objects.select_related('id_user', 'id_status'),
        id=freelancer_id
    )
    skills = FreelancerSkill.objects.select_related('id_skill').filter(id_freelancer=freelancer)
    portfolio = freelancer.portfolio_set.all()

    return render(request, 'freelancer_detail.html', {
        'freelancer': freelancer,
        'user': freelancer.id_user,  # пов'язаний користувач
        'skills': skills,
        'portfolio': portfolio,
    })
