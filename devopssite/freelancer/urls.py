from django.urls import path
from .views import (freelancer_list, freelancer_detail, get_portfolio,
                    user_freelancer_detail, update_freelancer_profile,
                    create_freelancer_profile, create_portfolio_item,
                    update_portfolio_item, delete_portfolio_item, get_user_portfolio,
                    analyze_resume_view)

app_name = 'freelancers'

urlpatterns = [
    path('freelancer_list/', freelancer_list, name='freelancer_list'),
    path('freelancer_detail/<int:freelancer_id>/', freelancer_detail, name='freelancer_detail'),
    path('get_portfolio/<int:portfolio_id>/', get_portfolio, name='get_portfolio'),
    path('get_user_portfolio/<int:portfolio_id>/', get_user_portfolio, name='get_user_portfolio'),
    path('user_freelancer_detail/', user_freelancer_detail, name='user_freelancer_detail'),
    path('update_freelancer_profile/', update_freelancer_profile, name='update_freelancer_profile'),
    path('freelancer/create/', create_freelancer_profile, name='create_freelancer_profile'),
    path('freelancer/portfolio/create/', create_portfolio_item, name='create_portfolio'),
    path('freelancer/portfolio/<int:item_id>/edit/', update_portfolio_item, name='update_portfolio'),
    path('freelancer/portfolio/<int:item_id>/delete/', delete_portfolio_item, name='delete_portfolio'),
    path('freelancer/analyze_resume/', analyze_resume_view, name='analyze_resume'),


]