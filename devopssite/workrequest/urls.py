from django.urls import path
from .views import employer_work_request, freelancer_work_request, change_request_status, create_work_request

app_name = 'workrequest'

urlpatterns = [
    path('employer_request/', employer_work_request, name='employer_request'),
    path('freelancer_request/', freelancer_work_request, name='freelancer_request'),
    path('change_request_status/<int:project_id>/<int:freelancer_id>/', change_request_status, name='change_request_status'),
    path('create_work_request/<int:project_id>/', create_work_request, name='create_work_request'),
]