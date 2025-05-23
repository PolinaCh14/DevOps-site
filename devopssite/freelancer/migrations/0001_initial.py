# Generated by Django 5.1.7 on 2025-04-07 19:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('skill', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FreelancerStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'freelancer_status',
            },
        ),
        migrations.CreateModel(
            name='Freelancer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cv', models.CharField(blank=True, null=True)),
                ('experience', models.IntegerField(blank=True, null=True)),
                ('id_user', models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('id_status', models.ForeignKey(db_column='id_status', on_delete=django.db.models.deletion.DO_NOTHING, to='freelancer.freelancerstatus')),
            ],
            options={
                'db_table': 'freelancer',
            },
        ),
        migrations.CreateModel(
            name='FreelancerSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_freelancer', models.ForeignKey(db_column='id_freelancer', on_delete=django.db.models.deletion.CASCADE, to='freelancer.freelancer')),
                ('id_skill', models.ForeignKey(db_column='id_skill', on_delete=django.db.models.deletion.DO_NOTHING, to='skill.skill')),
            ],
            options={
                'db_table': 'freelancer_skill',
            },
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('photo', models.CharField(blank=True, max_length=300, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('url', models.CharField(blank=True, max_length=100, null=True)),
                ('id_freelancer', models.ForeignKey(db_column='id_freelancer', on_delete=django.db.models.deletion.CASCADE, to='freelancer.freelancer')),
            ],
            options={
                'db_table': 'portfolio',
            },
        ),
    ]
