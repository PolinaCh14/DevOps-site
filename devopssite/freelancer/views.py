from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Freelancer, FreelancerStatus, FreelancerSkill, Portfolio
from skill.models import Skill
from users.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rating.utils import get_average_rating_for_user
from django.http import JsonResponse
from .utils import analyze_resume
import markdown


def get_all_portfolio(request, freelancer_id):
    portfolio = Portfolio.objects.filter(id_freelancer = freelancer_id)
    return render()

def get_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    freelancer = get_object_or_404(Freelancer, id=portfolio.id_freelancer.id)
    return render(request, 'portfolio.html', {'portfolio': portfolio, 'freelancer': freelancer})

def get_user_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    freelancer = get_object_or_404(Freelancer, id=portfolio.id_freelancer.id)
    return render(request, 'user_portfolio.html', {'portfolio': portfolio, 'freelancer': freelancer})

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
        url = request.POST.get('url')

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

    return render(request, 'freelancer_list.html', context)


def freelancer_detail(request, freelancer_id):
    freelancer = get_object_or_404(
        Freelancer.objects.select_related('id_user', 'id_status'),
        id=freelancer_id
    )
    raw_rating = get_average_rating_for_user(int(freelancer.id_user.id))
    rating = round(raw_rating) if raw_rating is not None else 0
    skills = FreelancerSkill.objects.select_related('id_skill').filter(id_freelancer=freelancer)
    portfolio = freelancer.portfolio_set.all()

    return render(request, 'freelancer_detail.html', {
        'freelancer': freelancer,
        'freelancer_user': freelancer.id_user,
        'skills': skills,
        'portfolio': portfolio,
        'rating': rating,
    })

@login_required
def user_freelancer_detail(request):
    try:
        freelancer = Freelancer.objects.select_related('id_user', 'id_status').get(id_user=request.user)
        skills = FreelancerSkill.objects.select_related('id_skill').filter(id_freelancer=freelancer)
        portfolio = freelancer.portfolio_set.all()
        rating = round(get_average_rating_for_user(request.user.id))

        return render(request, 'user_freelancer_detail.html', {
            'freelancer': freelancer,
            'user': freelancer.id_user,
            'skills': skills,
            'portfolio': portfolio,
            'rating': rating,
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

        selected_skill_ids = request.POST.getlist('skills')

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



def render_resume_feedback(raw_markdown):
    html = markdown.markdown(raw_markdown, extensions=['fenced_code'])
    return html


@login_required
def analyze_resume_view(request):
    freelancer = get_object_or_404(Freelancer, id_user=request.user)

    if request.method == "POST":
        pass
        cv_url = freelancer.cv
        if not cv_url:
            return JsonResponse({"error": "CV не знайдено."}, status=400)

        try:
            analysis_result = analyze_resume(cv_url, int(freelancer.id))
            rendered_html = render_resume_feedback(analysis_result)
            return JsonResponse({"analysis": rendered_html})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # GET-запит
    has_cv = bool(freelancer.cv)
    return render(request, 'analyze_resume.html', {
        'freelancer': freelancer,
        'has_cv': has_cv,
    })




