from django.urls import path
from .views import chat_page, chat_list_view, delete_chat_view

urlpatterns = [
    path('chats/', chat_list_view, name='chat_list'),
    path('<int:id>/', chat_page, name='chat_page'),
    path('delete_chat_view/<int:user_id>/', delete_chat_view, name='delete_chat_view'),
]
