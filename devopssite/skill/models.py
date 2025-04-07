from django.db import models

class Skill(models.Model):
    skill = models.CharField(unique=True, max_length=20)

    class Meta:
        db_table = 'skill'