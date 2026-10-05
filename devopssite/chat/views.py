from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Message
from django.contrib import messages

User = get_user_model()

@login_required
def chat_page(request, id):
    try:
        other_user = User.objects.get(id=id)
    except User.DoesNotExist:
        messages.error(request, "Користувача не знайдено.")
        return redirect('chat_list')

    return render(request, 'chat.html', {'other_user': other_user})

@login_required
def chat_list_view(request):
    user = request.user
    query = request.GET.get('q', '').strip().lower()

    messages = Message.objects.filter(
        (Q(sender=user) & Q(deleted_by_sender=False)) |
        (Q(receiver=user) & Q(deleted_by_receiver=False))
    )

    conversation_users = set()
    for msg in messages:
        if msg.sender != user:
            conversation_users.add(msg.sender)
        if msg.receiver != user:
            conversation_users.add(msg.receiver)

    if query:
        conversation_users = {
            u for u in conversation_users
            if query in u.first_name.lower() or query in u.last_name.lower()
        }

    return render(request, 'chat_list.html', {
        'conversations': conversation_users,
        'query': request.GET.get('q', '')
    })
@login_required
def delete_chat_view(request, user_id):
    if request.method == "POST":
        current_user = request.user
        other_user = get_object_or_404(User, id=user_id)

        Message.objects.filter(sender=current_user, receiver=other_user).update(deleted_by_sender=True)
        Message.objects.filter(sender=other_user, receiver=current_user).update(deleted_by_receiver=True)

        messages_to_delete = Message.objects.filter(
            (Q(sender=current_user, receiver=other_user) | Q(sender=other_user, receiver=current_user)),
            deleted_by_sender=True,
            deleted_by_receiver=True
        )
        messages_to_delete.delete()

    return redirect('chat_list')