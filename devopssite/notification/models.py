from django.db import models
from django.conf import settings


class NotificationType(models.Model):
    type = models.CharField(max_length=20)

    class Meta:
        db_table = 'notification_type'


class Notification(models.Model):
    id_receiver = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id_receiver')
    id_sender = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column='id_sender', related_name='notification_id_sender_set')
    id_type = models.ForeignKey('NotificationType', models.DO_NOTHING, db_column='id_type')
    message = models.CharField(max_length=500)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'notification'


