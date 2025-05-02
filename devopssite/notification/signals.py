from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, NotificationType
from workrequest.models import WorkRequest
from django.utils import timezone
from project.models import Project
from django.shortcuts import get_object_or_404

from .tasks import (
    send_notification_email,
)




@receiver(post_save, sender=WorkRequest)
def create_notification_on_work_request(sender, instance, created, **kwargs):
    if not created:
        print("Created WorkRequest — skipping update")
        return

    freelancer = instance.id_freelancer.id_user
    project = get_object_or_404(Project, id=instance.id_project.id)
    employer = project.user


    notif_type, _ = NotificationType.objects.get_or_create(id=1)

    message = f"{freelancer.name} {freelancer.surname} sent a collaboration request on your project."

    Notification.objects.create(
        id_sender=freelancer,
        id_receiver=employer,
        id_type=notif_type,
        message=message,
        created_at=timezone.now()
    )



@receiver(post_save, sender=WorkRequest)
def notify_freelancer_on_status_change(sender, instance, created, **kwargs):
    if created:
        return

    freelancer = instance.id_freelancer.id_user
    project = instance.id_project
    employer = project.user


    notif_type, _ = NotificationType.objects.get_or_create(id=2)

    message = f"Your request to collaborate on '{project.name}' was updated. New status: {instance.id_status.status}"

    notification = Notification.objects.create(
        id_sender=employer,
        id_receiver=freelancer,
        id_type=notif_type,
        message=message,
        created_at=timezone.now()
    )




@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Send an email when new notification created"""
    if created:
        send_notification_email(notification_id=instance.id)