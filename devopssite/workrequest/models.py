from django.db import models

# Create your models here.
class WorkRequestStatus(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'work_request_status'


class WorkRequest(models.Model):
    id_status = models.ForeignKey('WorkRequestStatus', models.DO_NOTHING, db_column='id_status')
    id_freelancer = models.ForeignKey('freelancer.Freelancer', models.SET_NULL, db_column='id_freelancer', null=True, blank=True)
    id_project = models.ForeignKey('project.Project', models.SET_NULL, db_column='id_project', null=True, blank=True)
    created_at = models.DateField()


    class Meta:
        db_table = 'work_request'
