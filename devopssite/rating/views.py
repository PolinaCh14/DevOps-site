from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Rating
from project.models import Project
from users.models import User
from decimal import Decimal
from workrequest.models import WorkRequest
from freelancer.models import Freelancer

@login_required
def create_rating(request, project_id, evaluates_id):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')

        try:
            rating_decimal = Decimal(rating_value)
            if rating_decimal < 0 or rating_decimal > 5:
                messages.error(request, "Оцінка повинна бути між 0 і 5.")
                return redirect('projects:user_project', project_id=project_id)
        except:
            messages.error(request, "Некоректне значення оцінки.")
            return redirect('projects:user_project', project_id=project_id)

        if request.user.id != evaluates_id:

            existing_rating = Rating.objects.filter(
                id_appraiser=request.user,
                id_evaluates_id=evaluates_id,
                id_project_id=project_id
            ).first()

            if existing_rating:
                messages.error(request, "Ви вже оцінили цього користувача для цього проєкту.")
                return redirect('projects:user_project', project_id=project_id)

            Rating.objects.create(
                id_appraiser=request.user,
                id_evaluates_id=evaluates_id,
                id_project_id=project_id,
                rating=rating_decimal
            )

            messages.success(request, "Оцінка успішно додана.")
            return redirect('projects:user_project', project_id=project_id)

        else:
            work_request = WorkRequest.objects.filter(
                id_project_id=project_id,
                id_status_id=2
            ).first()

            evaluates_id = work_request.id_freelancer.id_user_id

            existing_rating = Rating.objects.filter(
                id_appraiser=request.user,
                id_evaluates_id=evaluates_id,
                id_project_id=project_id
            ).first()

            if existing_rating:
                messages.error(request, "Ви вже оцінили цього користувача для цього проєкту.")
                return redirect('projects:user_project', project_id=project_id)

            # Створення рейтингу
            Rating.objects.create(
                id_appraiser=request.user,
                id_evaluates_id=evaluates_id,
                id_project_id=project_id,
                rating=rating_decimal
            )

            messages.success(request, "Оцінка успішно додана.")
            return redirect('projects:user_project', project_id=project_id)

    return render(request, 'create_rating.html', {
        'project_id': project_id,
        'evaluates_id': evaluates_id
    })



