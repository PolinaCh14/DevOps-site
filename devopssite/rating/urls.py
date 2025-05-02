from django.urls import path
from .views import create_rating

app_name = 'rating'

urlpatterns = [
    path('create_rating/<int:project_id>/<int:evaluates_id>/', create_rating, name='create_rating'),


]