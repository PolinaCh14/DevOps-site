from django.urls import path
from .views import (get_all_user, user_profile, update_user_profile,
                    delete_user, update_project, projects_search_view,
                    freelancer_list)

app_name = 'adminp'

urlpatterns = [
    path('users/', get_all_user, name='all_users'),
    path('user_profile/<int:id>/', user_profile, name='user_profile_a'),
    path('update_user_profile/<int:id>/', update_user_profile, name='update_user_profile_a'),
    path('delete_user/<int:id>/', delete_user, name='delete_user_a'),
    path('update_project/<int:project_id>/', update_project, name='update_project_a'),
    path('all_u_projects/', projects_search_view, name="projects_search_view_a"),
    path('freelancer_list/', freelancer_list, name="freelancer_list_a"),

]
