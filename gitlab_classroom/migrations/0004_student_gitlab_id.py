# Generated by Django 4.2.7 on 2024-04-19 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab_classroom', '0003_remove_student_gitlab_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='gitlab_id',
            field=models.CharField(default=0, max_length=255, unique=True),
        ),
    ]
