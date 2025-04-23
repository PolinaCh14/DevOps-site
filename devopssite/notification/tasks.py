import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from .models import Notification, NotificationType
from devopssite.settings import DEFAULT_FROM_EMAIL



@shared_task
def create_notification(investor_id, startup_id, type_, message_id=None, project_id=None):
    """Create notification instance"""
    try:
        Notification.objects.create(
            notification_type=type_,
            investor_id=investor_id,
            startup_id=startup_id,
            project_id=project_id,
            message_id=message_id
        )
    except Exception as e:
        print(e)


def send_notification_email(notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)

        sender = notification.id_sender
        receiver = notification.id_receiver

        subject = "New Collaboration Request"
        message = notification.message

        profile_url = f"https://yourapp.com/profile/{sender.id}"

        html_message = render_email_html_message(
            recipient=f"{receiver.surname}",
            message=message,
            profile_url=profile_url,
            profile_type='freelancer'
        )

        print(f"Receiver email: {receiver.email}")
        send_mail(
            subject=subject,
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[receiver.email],
            html_message=html_message,
            fail_silently=False
        )

    except Exception as e:
        print("Сталася помилка під час надсилання email:")
        print(repr(e))

def render_email_html_message(recipient, message, profile_url, profile_type):
    return f'''
    <p>Hello, {recipient}</p>
    <p>{message}</p>
    <p><a href="{profile_url}">View {profile_type}'s profile</a></p>
    <p>Thank you for choosing Forum!</p>
    '''

def render_email_html_message_status(recipient, message, profile_url, profile_type):
    return f'''
    <p>Hello, {recipient}</p>
    <p>{message}</p>
    <p><a href="{profile_url}">View {profile_type}'s profile</a></p>
    <p>Thank you for choosing Forum!</p>
    '''
