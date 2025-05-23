# Generated by Django 5.1.7 on 2025-04-20 17:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'notification_type',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('id_receiver', models.ForeignKey(db_column='id_receiver', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('id_sender', models.ForeignKey(db_column='id_sender', on_delete=django.db.models.deletion.CASCADE, related_name='notification_id_sender_set', to=settings.AUTH_USER_MODEL)),
                ('id_type', models.ForeignKey(db_column='id_type', on_delete=django.db.models.deletion.DO_NOTHING, to='notification.notificationtype')),
            ],
            options={
                'db_table': 'notification',
            },
        ),
    ]
