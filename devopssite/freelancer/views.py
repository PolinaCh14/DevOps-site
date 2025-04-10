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

@login_required
def user_freelancer_detail(request):
    try:
        freelancer = Freelancer.objects.select_related('id_user', 'id_status').get(id_user=request.user)
        skills = FreelancerSkill.objects.select_related('id_skill').filter(id_freelancer=freelancer)
        portfolio = freelancer.portfolio_set.all()

        return render(request, 'user_freelancer_detail.html', {
            'freelancer': freelancer,
            'user': freelancer.id_user,
            'skills': skills,
            'portfolio': portfolio,
        })
    except Freelancer.DoesNotExist:
        print("error")
        return render(request, 'user_freelancer_detail.html', {
            'freelancer': None,
            'user': request.user,
        })

@login_required
def update_freelancer_profile(request):
    freelancer = get_object_or_404(Freelancer, id_user=request.user)
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

        selected_skill_ids = request.POST.getlist('skills')  # список checkbox-значень

        FreelancerSkill.objects.filter(id_freelancer=freelancer).delete()

        for skill_id in selected_skill_ids:
            try:
                skill_obj = Skill.objects.get(id=int(skill_id))
                FreelancerSkill.objects.create(id_freelancer=freelancer, id_skill=skill_obj)
            except (Skill.DoesNotExist, ValueError):
                continue

        return redirect('freelancers:user_freelancer_detail')

    existing_skill_ids = FreelancerSkill.objects.filter(id_freelancer=freelancer).values_list('id_skill_id', flat=True)

    return render(request, 'freelancer_profile_edit.html', {
        'freelancer': freelancer,
        'statuses': statuses,
        'skills': all_skills,
        'existing_skill_ids': existing_skill_ids,
    })


@login_required
def create_freelancer_profile(request):
    # Якщо профіль уже існує — редирект на деталі
    if Freelancer.objects.filter(id_user=request.user).exists():
        return redirect('freelancers:user_freelancer_detail')

    statuses = FreelancerStatus.objects.all()
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        cv = request.POST.get('cv', '')
        experience = request.POST.get('experience', 0)
        status_id = request.POST.get('status')
        selected_skill_ids = request.POST.getlist('skills')

        try:
            experience = int(experience)
        except ValueError:
            experience = 0

        freelancer = Freelancer.objects.create(
            id_user=request.user,
            cv=cv,
            experience=experience,
            id_status_id=int(status_id) if status_id and status_id.isdigit() else None
        )

        for skill_id in selected_skill_ids:
            try:
                skill_obj = Skill.objects.get(id=int(skill_id))
                FreelancerSkill.objects.create(id_freelancer=freelancer, id_skill=skill_obj)
            except (Skill.DoesNotExist, ValueError):
                continue

        return redirect('freelancers:user_freelancer_detail')

    return render(request, 'freelancer_profile_create.html', {
        'statuses': statuses,
        'skills': all_skills,
    })

@login_required
def create_portfolio_item(request):
    freelancer = get_object_or_404(Freelancer, id_user=request.user)

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
            return redirect('freelancers:user_freelancer_detail')

    return render(request, 'portfolio_create.html')


@login_required
def update_portfolio_item(request, item_id):
    portfolio_item = get_object_or_404(Portfolio, id=item_id, id_freelancer__id_user=request.user)

    if request.method == 'POST':
        portfolio_item.title = request.POST.get('title', '').strip()
        portfolio_item.description = request.POST.get('description', '').strip()
        portfolio_item.photo = request.POST.get('photo', '').strip()
        portfolio_item.url = request.POST.get('url', '').strip()
        portfolio_item.save()

        return redirect('freelancers:user_freelancer_detail')

    return render(request, 'portfolio_update.html', {
        'item': portfolio_item
    })

@login_required
def delete_portfolio_item(request, item_id):
    portfolio_item = get_object_or_404(Portfolio, id=item_id, id_freelancer__id_user=request.user)

    if request.method == 'POST':
        portfolio_item.delete()
        return redirect('freelancers:user_freelancer_detail')

    return render(request, 'portfolio_confirm_delete.html', {
        'item': portfolio_item
    })