from django.urls import path
from .views import (users_project_view,
                    all_project_view,
                    users_projects_view,
                    user_projects_search_view,
                    project_view,
                    projects_search_view)

app_name = 'projects'

urlpatterns = [
    path('users_projects/', users_projects_view, name='user_projects'),
    path('user_project/<int:project_id>/', users_project_view, name='user_project'),
    path('user_projects_search_view/', user_projects_search_view, name='user_projects_search_view'),
    path('project/<int:project_id>/', project_view, name='project'),
    path('projects_search_view/', projects_search_view, name='projects_search_view'),

    # path('logout/', logout_view, name='logout'),
    # path('profile/', get_user, name='profile'),
    # path('update_profile/', update_user_profile, name='update_profile'),
]