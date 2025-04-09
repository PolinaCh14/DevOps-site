from django.urls import path
from .views import freelancer_list, freelancer_detail, get_portfolio

app_name = 'freelancers'

urlpatterns = [
    path('freelancer_list/', freelancer_list, name='freelancer_list'),
    path('freelancer_detail/<int:freelancer_id>/', freelancer_detail, name='freelancer_detail'),
    path('get_portfolio/<int:portfolio_id>/', get_portfolio, name='get_portfolio'),


]