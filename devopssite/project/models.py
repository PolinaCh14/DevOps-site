from django.db import models
from django.conf import settings

class Status(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'status'


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.ForeignKey('Status', models.DO_NOTHING)
    name = models.CharField(max_length=30, blank=False, null=False)
    description = models.CharField(max_length=500, blank=False, null=False)
    execution = models.IntegerField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    end_at = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'project'



class ProjectSkill(models.Model):
    id_skill = models.ForeignKey('skill.Skill', models.DO_NOTHING, db_column='id_skill')
    id_project = models.ForeignKey(Project, models.CASCADE, db_column='id_project')

    class Meta:
        db_table = 'project_skill'