from django.db import models
from django.conf import settings

class FreelancerStatus(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'freelancer_status'


class Freelancer(models.Model):
    id_user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column='id_user')
    id_status = models.ForeignKey('FreelancerStatus', models.DO_NOTHING, db_column='id_status')
    cv = models.CharField(blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'freelancer'


class FreelancerSkill(models.Model):
    id_skill = models.ForeignKey('skill.Skill', models.DO_NOTHING, db_column='id_skill')
    id_freelancer = models.ForeignKey(Freelancer, models.CASCADE, db_column='id_freelancer')

    class Meta:
        db_table = 'freelancer_skill'

class Portfolio(models.Model):
    id_freelancer = models.ForeignKey(Freelancer, models.CASCADE, db_column='id_freelancer')
    title = models.CharField(max_length=50, blank=False, null=False)
    photo = models.CharField(max_length=300, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'portfolio'