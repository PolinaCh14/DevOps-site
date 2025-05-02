from django.db import models

# Create your models here.
class WorkRequestStatus(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'work_request_status'


class WorkRequest(models.Model):
    id_status = models.ForeignKey('WorkRequestStatus', models.DO_NOTHING, db_column='id_status')
    id_freelancer = models.ForeignKey('freelancer.Freelancer', models.DO_NOTHING, db_column='id_freelancer')
    id_project = models.ForeignKey('project.Project', models.DO_NOTHING, db_column='id_project')
    created_at = models.DateField()

    class Meta:
        db_table = 'work_request'
