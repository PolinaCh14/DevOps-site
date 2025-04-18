from django.db import models
from django.conf import settings

# Create your models here.
class Rating(models.Model):
    id_evaluates = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id_evaluates')
    id_appraiser = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column='id_appraiser', related_name='rating_id_appraiser_set')
    id_project = models.ForeignKey('project.Project', models.DO_NOTHING, db_column='id_project')
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'rating'