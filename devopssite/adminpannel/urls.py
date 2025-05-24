from django.urls import path
from .views import (get_all_user, user_profile, update_user_profile,
                    delete_user, update_project, projects_search_view,
                    freelancer_list, freelancer_detail, update_freelancer_profile,
                    create_portfolio_item, update_portfolio_item, delete_portfolio_item,
                    get_user_portfolio, all_work_request)

app_name = 'adminp'

urlpatterns = [
    path('users/', get_all_user, name='all_users'),
    path('user_profile/<int:id>/', user_profile, name='user_profile_a'),
    path('update_user_profile/<int:id>/', update_user_profile, name='update_user_profile_a'),
    path('delete_user/<int:id>/', delete_user, name='delete_user_a'),
    path('update_project/<int:project_id>/', update_project, name='update_project_a'),
    path('all_u_projects/', projects_search_view, name="projects_search_view_a"),
    path('freelancer_list/', freelancer_list, name="freelancer_list_a"),
    path('freelancer_detail/<int:freelancer_id>/', freelancer_detail, name="freelancer_detail_a"),
    path('update_freelancer_profile/<int:freelancer_id>/', update_freelancer_profile, name="update_freelancer_profile_a"),
    path('create_portfolio_item/<int:freelancer_id>/', create_portfolio_item, name="create_portfolio_item_a"),
    path('update_portfolio_item/<int:item_id>/', update_portfolio_item, name="update_portfolio_item_a"),
    path('delete_portfolio_item/<int:item_id>/', delete_portfolio_item, name="delete_portfolio_item_a"),
    path('get_user_portfolio/<int:portfolio_id>/', get_user_portfolio, name="get_user_portfolio_a"),
    path('all_work_request/', all_work_request, name="all_work_request_a"),


]
