from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Role
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Користувач з такою поштою вже існує.')
            return render(request, 'register.html')

        role = Role.objects.get(id=request.POST['role_id'])

        user = User.objects.create_user(
            email=email,
            password=request.POST['password'],
            name=request.POST['name'],
            surname=request.POST['surname'],
            phone=request.POST['phone'],
            about_me=request.POST['about_me'],
            role=role
        )
        login(request, user)
        return redirect('home')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Невірна пошта або пароль')  # ось тут повідомлення

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required()
def get_user(request):
    user = request.user
    context = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "profile_picture": user.profile_picture,
        "role": user.role.role,
    }
    return render(request, 'user.page.html', context)

@login_required
def update_user_profile(request):
    user = request.user

    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        phone = request.POST.get('phone')
        about_me = request.POST.get('about_me')
        profile_picture = request.POST.get('profile_picture')

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

        if updated:
            user.save()

        return redirect('users:profile')

    return render(request, 'update_profile.html', {'user': user})