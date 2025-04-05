from django.urls import path
from .views import register_view, login_view, logout_view, get_user, update_user_profile

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', get_user, name='profile'),
    path('update_profile/', update_user_profile, name='update_profile'),
]
