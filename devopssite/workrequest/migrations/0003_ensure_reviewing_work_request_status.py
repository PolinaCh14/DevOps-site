from django.db import migrations


REVIEWING_STATUS = "На розгляді"


def ensure_reviewing_status(apps, schema_editor):
    WorkRequestStatus = apps.get_model("workrequest", "WorkRequestStatus")
    database = schema_editor.connection.alias
    matches = WorkRequestStatus.objects.using(database).filter(status=REVIEWING_STATUS)
    match_count = matches.count()

    if match_count > 1:
        raise RuntimeError(
            f"Expected at most one WorkRequestStatus labeled {REVIEWING_STATUS!r}."
        )
    if match_count == 0:
        WorkRequestStatus.objects.using(database).create(status=REVIEWING_STATUS)


class Migration(migrations.Migration):

    dependencies = [
        ("workrequest", "0002_alter_workrequest_id_freelancer_and_more"),
    ]

    operations = [
        migrations.RunPython(ensure_reviewing_status, migrations.RunPython.noop),
    ]
