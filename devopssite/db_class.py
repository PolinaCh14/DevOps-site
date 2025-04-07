
class WorkRequest(models.Model):
    id_status = models.ForeignKey('WorkRequestStatus', models.DO_NOTHING, db_column='id_status')
    id_freelancer = models.ForeignKey(Freelancer, models.DO_NOTHING, db_column='id_freelancer')
    id_project = models.ForeignKey(Project, models.DO_NOTHING, db_column='id_project')
    created_at = models.DateField()

    class Meta:
        managed = False
        db_table = 'work_request'


class WorkRequestStatus(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'work_request_status'


class Freelancer(models.Model):
    id_user = models.ForeignKey('User', models.DO_NOTHING, db_column='id_user')
    id_status = models.ForeignKey('FreelancerStatus', models.DO_NOTHING, db_column='id_status')
    cv = models.CharField(blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'freelancer'


class FreelancerSkill(models.Model):
    id_skill = models.ForeignKey('Skill', models.DO_NOTHING, db_column='id_skill')
    id_freelancer = models.ForeignKey(Freelancer, models.DO_NOTHING, db_column='id_freelancer')

    class Meta:
        managed = False
        db_table = 'freelancer_skill'


class FreelancerStatus(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'freelancer_status'


class Notification(models.Model):
    id_receiver = models.ForeignKey('User', models.DO_NOTHING, db_column='id_receiver')
    id_sender = models.ForeignKey('User', models.DO_NOTHING, db_column='id_sender', related_name='notification_id_sender_set')
    id_type = models.ForeignKey('NotificationType', models.DO_NOTHING, db_column='id_type')
    message = models.CharField(max_length=500)
    created_at = models.DateField()

    class Meta:
        managed = False
        db_table = 'notification'


class NotificationType(models.Model):
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'notification_type'


class Portfolio(models.Model):
    id_freelancer = models.ForeignKey(Freelancer, models.DO_NOTHING, db_column='id_freelancer')
    photo = models.CharField(max_length=30, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portfolio'



class Rating(models.Model):
    id_evaluates = models.ForeignKey('User', models.DO_NOTHING, db_column='id_evaluates')
    id_appraiser = models.ForeignKey('User', models.DO_NOTHING, db_column='id_appraiser', related_name='rating_id_appraiser_set')
    id_project = models.ForeignKey(Project, models.DO_NOTHING, db_column='id_project')
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rating'







