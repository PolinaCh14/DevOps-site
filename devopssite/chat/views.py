from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

@login_required
def chat_page(request, id):
    other_user = get_object_or_404(User, id=id)
    return render(request, 'chat.html', {'other_user': other_user})