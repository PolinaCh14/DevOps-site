from django.contrib import admin
from django.urls import path, include
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls')),
    path('projects/', include('project.urls')),
    path('freelancers/', include('freelancer.urls')),
    path('workrequest/', include('workrequest.urls')),
    path('rating/', include('rating.urls')),
]
