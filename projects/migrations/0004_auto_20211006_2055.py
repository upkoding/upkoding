# Generated by Django 3.1.6 on 2021-10-06 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20210912_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprojectevent',
            name='event_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'project_start'), (1, 'progress_update'), (2, 'progress_complete'), (3, 'review_request'), (10, 'review_message'), (11, 'project_complete'), (12, 'project_incomplete')]),
        ),
    ]
