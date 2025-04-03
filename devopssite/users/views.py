from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, Role
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        role = Role.objects.get(id=request.POST['role_id'])
        user = User.objects.create_user(
            email=request.POST['email'],
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
            print("login!!!!")
            return redirect('home')
        print("not login")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
