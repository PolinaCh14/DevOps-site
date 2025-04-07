from django.urls import path
from .views import (users_project_view,
                    create_project,
                    users_projects_view,
                    user_projects_search_view,
                    project_view,
                    projects_search_view,
                    project_delete,
                    update_project)

app_name = 'projects'

urlpatterns = [
    path('users_projects/', users_projects_view, name='user_projects'),
    path('user_project/<int:project_id>/', users_project_view, name='user_project'),
    path('user_projects_search_view/', user_projects_search_view, name='user_projects_search_view'),
    path('project/<int:project_id>/', project_view, name='project'),
    path('projects_search_view/', projects_search_view, name='projects_search_view'),
    path('create_project/', create_project, name='create_project'),
    path('project_delete/<int:project_id>/', project_delete, name='project_delete'),
    path('update_project/<int:project_id>/', update_project, name='update_project'),

]