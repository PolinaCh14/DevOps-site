from django.urls import path
from .views import chat_page

urlpatterns = [
    path('<int:id>/', chat_page, name='chat_page'),
]
